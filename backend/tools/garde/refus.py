"""Raison d'un refus de la garde, renvoyée à l'agent par Claude Code."""


def refus(agent: str, action: str) -> str:
    """Rédige la raison d'un refus.

    Le texte dit à l'agent quoi faire ensuite : ne pas chercher un autre chemin, mais signaler le
    besoin au coordinateur, seul habilité à modifier ce qui sort de la couche de l'agent.
    """
    return (
        f"L'agent « {agent} » n'a pas le droit {action}. Ne cherche pas à contourner : "
        "signale au coordinateur ce qu'il faut modifier, et pourquoi."
    )
