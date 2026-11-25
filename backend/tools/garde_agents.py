"""Garde des sous-agents : chacun n'écrit que dans sa couche, aucun ne modifie l'état de git.

Un hook Claude Code `PreToolUse` appelle ce script pour chaque appel de `Edit`, `Write` et
`Bash`, avec le JSON décrit par la documentation de Claude Code sur l'entrée standard :
- autorisé : code de sortie 0, rien sur la sortie standard ;
- refusé : une décision `deny` en JSON sur la sortie standard, code de sortie 0 ;
- entrée illisible : raison sur la sortie d'erreur, code de sortie 2 (mieux vaut bloquer).

La session principale (le coordinateur) n'a pas de `agent_type` : tout lui est permis, elle
doit pouvoir commiter. C'est une barrière contre les erreurs de bonne foi, pas contre la
malveillance : une écriture par un autre moyen (`python -c`, redirection `>`, script écrit
puis lancé) n'est pas vue.

Les chemins sont comparés comme du texte, de la même façon sous Windows (poste) et sous Linux
(CI). Seule la bibliothèque standard est utilisée : le script se lance par `python -I`, sans uv.
"""

import json
import os
import posixpath
import re
import shlex
import sys
from collections.abc import Iterator, Mapping
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

CODE_ENTREE_ILLISIBLE = 2
OUTILS_SURVEILLES = frozenset({"Edit", "Write", "Bash"})


def _mots(texte: str) -> tuple[str, ...]:
    """Découpe une liste écrite à plat (motifs, noms de commande) sur les espaces et les retours."""
    return tuple(texte.split())


# Droits d'écriture de chaque sous-agent (Edit et Write), en motifs relatifs à la racine du dépôt.
# Ils reprennent le découpage en couches des règles 01 à 07 et l'outillage de la règle 09. Un
# agent absent de cette table n'écrit nulle part dans le dépôt.
DROITS_ECRITURE: Mapping[str, tuple[str, ...]] = {
    "dev-metier": _mots("""
        backend/app/*/domain/** backend/app/*/application/**
        backend/app/*/infrastructure/memoire/** backend/app/shared/infrastructure/*_memoire.py
        backend/tests/domain/** backend/tests/application/** backend/tests/fabriques/**
    """),
    "dev-donnees": _mots("""
        backend/app/*/infrastructure/** backend/app/composition/** backend/app/cli/**
        backend/app/main.py backend/alembic.ini backend/migrations/**
        backend/tests/infrastructure/** backend/tests/contrats/** backend/tests/migrations/**
        backend/tests/integration/** backend/tests/composition/** backend/tests/conftest.py
    """),
    "dev-api": _mots("""
        backend/app/*/api/** backend/tests/api/**
        frontend/src/api/schema.d.ts frontend/openapi.json
    """),
    "dev-frontend": _mots("frontend/**"),
    "dev-socle": _mots("""
        deploy/** .github/** justfile .pre-commit-config.yaml
        .editorconfig .gitattributes .gitignore backend/.gitignore
        backend/tools/** backend/tests/outils/** backend/tests/architecture/**
        backend/pyproject.toml backend/uv.lock
        frontend/.gitignore frontend/.npmrc frontend/.prettierignore frontend/.prettierrc.json
        frontend/package.json frontend/pnpm-lock.yaml frontend/eslint/** frontend/eslint.config.js
        frontend/tsconfig*.json frontend/vite.config.ts frontend/vitest.setup.ts
        frontend/playwright.config.ts
    """),
}

# Exceptions aux droits : le client généré n'est jamais écrit à la main (ADR 0013).
EXCLUSIONS_ECRITURE: Mapping[str, tuple[str, ...]] = {
    "dev-frontend": _mots("frontend/src/api/schema.d.ts frontend/openapi.json"),
}

# Protégés pour tous les sous-agents, avant toute autre règle : un agent ne doit pas pouvoir
# élargir ses propres droits.
FICHIERS_PROTEGES = _mots(
    ".claude/** backend/tools/garde_agents.py backend/tests/outils/*garde_agents*.py"
)

# Ces agents n'ont ni Edit ni Write : un appel qui arrive quand même est refusé.
AGENTS_SANS_ECRITURE = _mots("revue conformite securite pentest backlog")
# Ces agents vérifient sans rien modifier : les commandes d'écriture leur sont aussi refusées.
VERIFICATEURS = _mots("revue conformite securite")

GIT_INTERDIT = _mots("commit push checkout reset stash switch restore rebase merge clean")
# Options globales de git qui consomment l'argument suivant, à sauter pour trouver la sous-commande.
OPTIONS_GIT_A_VALEUR = _mots("-C -c --git-dir --work-tree --namespace --config-env --super-prefix")
COMMANDES_D_ECRITURE = _mots("rm mv cp tee")
INTERPRETEURS_DE_COMMANDES = _mots("sh bash zsh dash")
# Mots qui précèdent une commande sans la changer : `if x; then git push` reste un `git push`.
MOTS_TRANSPARENTS = _mots("env command exec time nohup then do else ! { if while until")

# Un segment est une suite de textes cités (gardés d'un bloc) et de caractères ordinaires, que
# ne coupent ni `;`, `&`, `|`, retour à la ligne, accent grave, parenthèse ni `$(`.
_SEGMENT = re.compile(r"""(?:"(?:\\.|[^"\\])*"|'[^']*'|\$(?!\()|[^;&|\n`()$"'])+""")
_AFFECTATION = re.compile(r"[A-Za-z_][A-Za-z0-9_]*=")
_OPTION_C = re.compile(r"-[a-z]*c[a-z]*")
_OPTION_SED_SUR_PLACE = re.compile(r"-[A-Za-z]*i.*|--in-place(=.*)?")
_CHEMIN_ABSOLU = re.compile(r"[a-z]:/|/")


class EntreeIllisibleError(Exception):
    """L'entrée du hook n'a pas la forme décrite par la documentation de Claude Code."""


@dataclass(frozen=True)
class Reponse:
    """Ce que le script doit rendre à Claude Code : code de sortie et flux à écrire."""

    code: int
    sortie: str = ""
    erreur: str = ""


def normaliser(chemin: str) -> str:
    """Rend un chemin comparable : `/` partout, `.` et `..` résolus, casse ignorée."""
    return posixpath.normpath(chemin.replace("\\", "/")).casefold()


def chemin_relatif(chemin: str, racine: str | Path) -> str | None:
    """Donne le chemin relatif à la racine du dépôt, ou `None` s'il est hors du dépôt.

    Un chemin non absolu est rattaché à la racine. Le texte est comparé tel quel, sans toucher
    au disque : le résultat est le même sous Windows et sous Linux.
    """
    base = normaliser(str(racine)).rstrip("/")
    complet = normaliser(chemin)
    if not _CHEMIN_ABSOLU.match(complet):
        complet = normaliser(f"{base}/{chemin}")
    if complet == base:
        return "."
    prefixe = f"{base}/"
    return complet.removeprefix(prefixe) if complet.startswith(prefixe) else None


def _correspond(relatif: str, motifs: tuple[str, ...]) -> bool:
    return any(PurePosixPath(relatif).full_match(motif.casefold()) for motif in motifs)


def _refus(agent: str, action: str) -> str:
    return (
        f"L'agent « {agent} » n'a pas le droit {action}. Ne cherche pas à contourner : "
        "signale au coordinateur ce qu'il faut modifier, et pourquoi."
    )


def _raison_ecriture(agent: str, chemin: str, racine: str | Path) -> str | None:
    """Dit pourquoi l'écriture est refusée, ou renvoie `None` si elle est permise."""
    relatif = chemin_relatif(chemin, racine)
    if relatif is not None and _correspond(relatif, FICHIERS_PROTEGES):
        return _refus(agent, f"de modifier « {relatif} » : ce fichier de garde est protégé")
    if agent in AGENTS_SANS_ECRITURE:
        return _refus(agent, "d'écrire des fichiers")
    if relatif is None:
        # Hors du dépôt, seuls les agents sans table de droits (un agent généraliste) écrivent.
        return _refus(agent, "d'écrire hors du dépôt") if agent in DROITS_ECRITURE else None
    permis = _correspond(relatif, DROITS_ECRITURE.get(agent, ()))
    exclu = _correspond(relatif, EXCLUSIONS_ECRITURE.get(agent, ()))
    return None if permis and not exclu else _refus(agent, f"d'écrire dans « {relatif} »")


def _nom_commande(mot: str) -> str:
    """Nom d'une commande sans son dossier ni `.exe` : `/usr/bin/git` et `git.exe` donnent `git`."""
    return re.split(r"[\\/]", mot)[-1].casefold().removesuffix(".exe")


def _decouper(segment: str) -> list[str]:
    try:
        return shlex.split(segment)
    except ValueError:
        # Guillemet non fermé : on préfère lire la commande de travers que ne pas la lire.
        return segment.split()


def _sans_prefixes(mots: list[str]) -> list[str]:
    """Retire les affectations `NOM=valeur` et les mots transparents qui précèdent la commande."""
    debut = 0
    while debut < len(mots) and (
        _AFFECTATION.match(mots[debut]) or mots[debut] in MOTS_TRANSPARENTS
    ):
        debut += 1
    return mots[debut:]


def _script_du_shell(mots: list[str]) -> str | None:
    """Renvoie le texte passé à `sh -c`, `bash -c` ou `bash -lc`, pour l'examiner à son tour."""
    if _nom_commande(mots[0]) not in INTERPRETEURS_DE_COMMANDES:
        return None
    options = mots[1:]
    for position, option in enumerate(options[:-1]):
        if _OPTION_C.fullmatch(option):
            return options[position + 1]
    return None


def _commandes(texte: str) -> Iterator[list[str]]:
    """Énumère les commandes d'une ligne de shell, sous-shells et `bash -c` compris."""
    for segment in _SEGMENT.findall(texte):
        mots = _sans_prefixes(_decouper(segment))
        if not mots:
            continue
        yield mots
        script = _script_du_shell(mots)
        if script is not None:
            yield from _commandes(script)


def _sous_commande_git(arguments: list[str]) -> str:
    """Trouve la sous-commande de git, en sautant ses options globales (`-C chemin`…)."""
    suivants = iter(arguments)
    for argument in suivants:
        if argument in OPTIONS_GIT_A_VALEUR:
            next(suivants, None)
        elif not argument.startswith("-"):
            return argument
    return ""


def _raison_commande_unique(agent: str, mots: list[str]) -> str | None:
    nom, arguments = _nom_commande(mots[0]), mots[1:]
    sous_commande = _sous_commande_git(arguments) if nom == "git" else ""
    if sous_commande in GIT_INTERDIT:
        return _refus(agent, f"de lancer « git {sous_commande} » : seul le coordinateur commite")
    sed_sur_place = nom == "sed" and any(_OPTION_SED_SUR_PLACE.fullmatch(a) for a in arguments)
    if agent in VERIFICATEURS and (nom in COMMANDES_D_ECRITURE or sed_sur_place):
        return _refus(agent, f"de lancer « {nom} » : un vérificateur ne modifie rien")
    return None


def _raison_commande(agent: str, texte: str) -> str | None:
    """Dit pourquoi la commande est refusée, ou renvoie `None` si elle est permise."""
    raisons = (_raison_commande_unique(agent, mots) for mots in _commandes(texte))
    return next((raison for raison in raisons if raison is not None), None)


def _lire_objet(valeur: object, description: str) -> dict[str, object]:
    if not isinstance(valeur, dict):
        raise EntreeIllisibleError(f"{description} doit être un objet JSON")
    return valeur


def _lire_texte(objet: dict[str, object], nom: str, *, requis: bool) -> str:
    valeur = objet.get(nom)
    if valeur is None and not requis:
        return ""
    if not isinstance(valeur, str):
        raise EntreeIllisibleError(f"le champ « {nom} » doit être un texte")
    return valeur


def decider(entree: object, racine: str | Path) -> str | None:
    """Décide de l'appel d'un outil : `None` s'il est permis, sinon la raison du refus.

    Lève :
        EntreeIllisibleError : l'entrée n'a pas la forme attendue.
    """
    objet = _lire_objet(entree, "l'entrée")
    agent = _lire_texte(objet, "agent_type", requis=False)
    if not agent:
        return None
    outil = _lire_texte(objet, "tool_name", requis=True)
    if outil not in OUTILS_SURVEILLES:
        return None
    parametres = _lire_objet(objet.get("tool_input"), "tool_input")
    if outil == "Bash":
        return _raison_commande(agent, _lire_texte(parametres, "command", requis=True))
    return _raison_ecriture(agent, _lire_texte(parametres, "file_path", requis=True), racine)


def traiter(brut: bytes, racine: str | Path) -> Reponse:
    """Transforme l'entrée du hook (octets lus sur stdin) en réponse pour Claude Code."""
    try:
        raison = decider(json.loads(brut.decode("utf-8")), racine)
    except (ValueError, EntreeIllisibleError) as erreur:
        # `ValueError` couvre l'UTF-8 invalide et le JSON invalide : mieux vaut bloquer.
        return Reponse(
            CODE_ENTREE_ILLISIBLE, erreur=f"Garde des agents : entrée illisible ({erreur}).\n"
        )
    if raison is None:
        return Reponse(0)
    decision = {
        "hookEventName": "PreToolUse",
        "permissionDecision": "deny",
        "permissionDecisionReason": raison,
    }
    return Reponse(0, sortie=json.dumps({"hookSpecificOutput": decision}) + "\n")


def main() -> int:
    """Lit l'appel sur l'entrée standard et écrit la réponse ; renvoie le code de sortie."""
    racine = os.environ.get("CLAUDE_PROJECT_DIR") or Path(__file__).resolve().parents[2]
    reponse = traiter(sys.stdin.buffer.read(), racine)
    sys.stdout.write(reponse.sortie)
    sys.stderr.write(reponse.erreur)
    return reponse.code


if __name__ == "__main__":
    sys.exit(main())
