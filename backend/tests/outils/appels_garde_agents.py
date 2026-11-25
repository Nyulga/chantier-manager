"""Fabriques d'appels d'outils, partagées par les tests de la garde des sous-agents."""

RACINE = "C:/Users/X/Projet"


def ecriture(agent: str, relatif: str, outil: str = "Write") -> dict[str, object]:
    """Appel d'écriture sur un chemin du dépôt, donné relativement à la racine."""
    return {
        "agent_type": agent,
        "tool_name": outil,
        "tool_input": {"file_path": f"{RACINE}/{relatif}"},
    }


def commande(agent: str, texte: str) -> dict[str, object]:
    """Appel de l'outil Bash avec la commande donnée."""
    return {"agent_type": agent, "tool_name": "Bash", "tool_input": {"command": texte}}
