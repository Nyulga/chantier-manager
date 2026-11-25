"""Protocole du hook `PreToolUse` : lire l'appel envoyé par Claude Code et former la réponse.

L'entrée est le JSON décrit par la documentation de Claude Code. Trois réponses possibles :
- autorisé : code de sortie 0, rien sur la sortie standard ;
- refusé : une décision `deny` en JSON sur la sortie standard, code de sortie 0 ;
- bloqué : raison sur la sortie d'erreur, code de sortie 2 (le seul que Claude Code lit comme un
  blocage).
"""

import json
from dataclasses import dataclass
from pathlib import Path

from tools.garde.commandes import raison_commande
from tools.garde.droits import raison_ecriture

CODE_BLOQUER = 2
OUTILS_SURVEILLES = frozenset({"Edit", "Write", "Bash"})


class EntreeIllisibleError(Exception):
    """L'entrée du hook n'a pas la forme décrite par la documentation de Claude Code."""


@dataclass(frozen=True)
class Reponse:
    """Ce que le script doit rendre à Claude Code : code de sortie et flux à écrire."""

    code: int
    sortie: str = ""
    erreur: str = ""


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

    La session principale (le coordinateur) n'a pas de `agent_type` : tout lui est permis, car
    elle doit pouvoir commiter.

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
        return raison_commande(agent, _lire_texte(parametres, "command", requis=True))
    return raison_ecriture(agent, _lire_texte(parametres, "file_path", requis=True), racine)


def traiter(brut: bytes, racine: str | Path) -> Reponse:
    """Transforme l'entrée du hook (les octets lus sur l'entrée standard) en réponse."""
    try:
        raison = decider(json.loads(brut.decode("utf-8")), racine)
    except (ValueError, EntreeIllisibleError) as erreur:
        # `ValueError` couvre l'UTF-8 invalide et le JSON invalide : mieux vaut bloquer.
        return Reponse(CODE_BLOQUER, erreur=f"Garde des agents : entrée illisible ({erreur}).\n")
    except Exception as erreur:
        # Une garde en panne (commande imbriquée à l'excès, cas non prévu) ne doit jamais laisser
        # passer un appel qu'elle n'a pas su juger : on bloque, avec le nom de l'erreur.
        message = f"Garde des agents : erreur interne ({type(erreur).__name__}).\n"
        return Reponse(CODE_BLOQUER, erreur=message)
    if raison is None:
        return Reponse(0)
    decision = {
        "hookEventName": "PreToolUse",
        "permissionDecision": "deny",
        "permissionDecisionReason": raison,
    }
    return Reponse(0, sortie=json.dumps({"hookSpecificOutput": decision}) + "\n")
