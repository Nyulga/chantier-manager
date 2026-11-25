"""Analyse des commandes Bash des sous-agents : git en lecture, gh, écritures des vérificateurs.

Pour git, la garde suit une liste blanche : un sous-agent ne lance que des sous-commandes qui lisent
le dépôt. Toute autre sous-commande (commit, pull, add, config…) revient au coordinateur, seul à
modifier l'état du dépôt (skill `lot`).
"""

import re
import shlex
from collections.abc import Iterator, Mapping

from tools.garde.refus import refus

# Ces agents vérifient sans rien modifier : les commandes d'écriture leur sont aussi refusées.
VERIFICATEURS = ("revue", "conformite", "securite")

GIT_LECTURE = frozenset(
    (
        "status",
        "diff",
        "log",
        "show",
        "ls-files",
        "grep",
        "blame",
        "rev-parse",
        "check-ignore",
        "shortlog",
        "describe",
        "merge-base",
        "rev-list",
        "cat-file",
        "ls-tree",
        "for-each-ref",
        "help",
        "version",
    )
)
# Sous-commandes qui ne lisent qu'avec certaines options : `git branch` liste les branches, mais
# `git branch x` en crée une et `git branch -D x` en supprime une.
GIT_LECTURE_AVEC_OPTIONS: Mapping[str, frozenset[str]] = {
    "branch": frozenset(
        ("--show-current", "--list", "-a", "-r", "-v", "-vv", "--all", "--remotes")
    ),
    "remote": frozenset({"-v", "--verbose"}),
}
# Options globales de git qui consomment l'argument suivant, à sauter pour trouver la sous-commande.
OPTIONS_GIT_A_VALEUR = frozenset(
    ["-C", "-c", "--git-dir", "--work-tree", "--namespace", "--config-env", "--super-prefix"]
)
# `gh pr checkout` change de branche et `gh pr merge` fusionne : deux actions du coordinateur.
GH_INTERDIT = frozenset({("pr", "checkout"), ("pr", "merge")})
COMMANDES_D_ECRITURE = frozenset({"rm", "mv", "cp", "tee"})
INTERPRETEURS_POSIX = frozenset({"sh", "bash", "zsh", "dash"})
# PowerShell et cmd prennent tout le reste de la ligne comme commande, après `-Command` ou `/c`.
INTERPRETEURS_WINDOWS = frozenset({"powershell", "pwsh", "cmd"})
OPTIONS_COMMANDE_WINDOWS = frozenset({"-command", "-c", "/c", "/k"})
# Mots qui précèdent une commande sans la changer : `if x; then git push` reste un `git push`.
MOTS_TRANSPARENTS = frozenset(
    (
        "env",
        "command",
        "exec",
        "time",
        "nohup",
        "then",
        "do",
        "else",
        "!",
        "{",
        "if",
        "while",
        "until",
    )
)
# Commandes qui en lancent une autre, placée après leurs propres options : `xargs -n 1 git push`.
LANCEURS = frozenset({"xargs", "timeout", "sudo", "nice"})

# Un segment est une suite de textes cités (gardés d'un bloc) et de caractères ordinaires, que
# ne coupent ni `;`, `&`, `|`, retour à la ligne, accent grave, parenthèse ni `$(`.
_SEGMENT = re.compile(r"""(?:"(?:\\.|[^"\\])*"|'[^']*'|\$(?!\()|[^;&|\n`()$"'])+""")
# Une barre oblique inverse en fin de ligne prolonge la commande sur la ligne suivante.
_SUITE_DE_LIGNE = re.compile(r"\\\r?\n")
_AFFECTATION = re.compile(r"[A-Za-z_][A-Za-z0-9_]*=")
# Arguments propres à un lanceur : une option (`-n`), un nombre ou une durée (`1`, `60s`), `{}`.
_ARGUMENT_DE_LANCEUR = re.compile(r"-.*|\d+(\.\d+)?[smhd]?|\{\}")
# Option de `sh` qui annonce un script en ligne : `-c`, ou regroupée avec d'autres (`-lc`).
_OPTION_C = re.compile(r"-[a-z]*c[a-z]*")
# Option de `sed` qui modifie le fichier sur place : `-i`, `-i.bak`, `-ni` ou `--in-place`.
_OPTION_SED_SUR_PLACE = re.compile(r"-[A-Za-z]*i.*|--in-place(=.*)?")


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
    """Retire ce qui précède la vraie commande : `NOM=valeur`, mots transparents, lanceurs."""
    debut = 0
    while debut < len(mots):
        mot = mots[debut]
        if _AFFECTATION.match(mot) or mot in MOTS_TRANSPARENTS:
            debut += 1
        elif _nom_commande(mot) in LANCEURS:
            debut += 1
            while debut < len(mots) and _ARGUMENT_DE_LANCEUR.fullmatch(mots[debut]):
                debut += 1
        else:
            break
    return mots[debut:]


def _script_du_shell(mots: list[str]) -> str | None:
    """Renvoie le texte passé à un interpréteur (`bash -c`, `powershell -Command`, `cmd /c`)."""
    nom, options = _nom_commande(mots[0]), mots[1:]
    if nom in INTERPRETEURS_POSIX:
        position = next((i for i, o in enumerate(options[:-1]) if _OPTION_C.fullmatch(o)), None)
        return None if position is None else options[position + 1]
    if nom in INTERPRETEURS_WINDOWS:
        lancement = (i for i, o in enumerate(options) if o.casefold() in OPTIONS_COMMANDE_WINDOWS)
        position = next(lancement, None)
        return None if position is None else " ".join(options[position + 1 :])
    return None


def _commandes(texte: str) -> Iterator[list[str]]:
    """Énumère les commandes d'une ligne de shell, sous-shells et interpréteurs compris."""
    for segment in _SEGMENT.findall(_SUITE_DE_LIGNE.sub(" ", texte)):
        mots = _sans_prefixes(_decouper(segment))
        if not mots:
            continue
        yield mots
        script = _script_du_shell(mots)
        if script is not None:
            yield from _commandes(script)


def _sous_commande_git(arguments: list[str]) -> tuple[str, list[str]]:
    """Sépare la sous-commande de git de ses arguments, en sautant les options globales."""
    position = 0
    while position < len(arguments):
        argument = arguments[position]
        if argument in OPTIONS_GIT_A_VALEUR:
            position += 2
        elif argument.startswith("-"):
            position += 1
        else:
            return argument, arguments[position + 1 :]
    return "", []


def _git_ne_fait_que_lire(sous_commande: str, arguments: list[str]) -> bool:
    if any(argument.startswith("--output") for argument in arguments):
        return False  # `git diff --output=f` et `git log --output f` écrivent un fichier.
    if not sous_commande or sous_commande in GIT_LECTURE:
        return True
    options_permises = GIT_LECTURE_AVEC_OPTIONS.get(sous_commande)
    return options_permises is not None and set(arguments) <= options_permises


def _raison_git(agent: str, arguments: list[str]) -> str | None:
    sous_commande, reste = _sous_commande_git(arguments)
    if _git_ne_fait_que_lire(sous_commande, reste):
        return None
    return refus(agent, f"de lancer « git {sous_commande} » : seul le coordinateur modifie git")


def _raison_commande_unique(agent: str, mots: list[str]) -> str | None:
    nom, arguments = _nom_commande(mots[0]), mots[1:]
    if nom == "git":
        return _raison_git(agent, arguments)
    if nom == "gh" and tuple(arguments[:2]) in GH_INTERDIT:
        return refus(agent, f"de lancer « gh {' '.join(arguments[:2])} » : c'est au coordinateur")
    sed_sur_place = nom == "sed" and any(_OPTION_SED_SUR_PLACE.fullmatch(a) for a in arguments)
    if agent in VERIFICATEURS and (nom in COMMANDES_D_ECRITURE or sed_sur_place):
        return refus(agent, f"de lancer « {nom} » : un vérificateur ne modifie rien")
    return None


def raison_commande(agent: str, texte: str) -> str | None:
    """Dit pourquoi la commande est refusée, ou renvoie `None` si elle est permise."""
    raisons = (_raison_commande_unique(agent, mots) for mots in _commandes(texte))
    return next((raison for raison in raisons if raison is not None), None)
