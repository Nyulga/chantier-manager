"""Politiques d'accès du module étapes : des fonctions pures qui ne lèvent rien.

Dans le squelette, il n'y a pas encore d'affectation : les droits ne dépendent que
du rôle. En phase 2, ils dépendront aussi des chantiers de l'acteur (intent.md, §1).
"""

from app.etapes.domain.cycle import StatutEtape, actions_permises
from app.shared.domain.acteur import Acteur


def peut_lister_etapes_a_valider(acteur: Acteur) -> bool:
    """Dit si l'acteur peut consulter la file des étapes à valider.

    Cette file ne sert qu'à valider ou à refuser. Elle est donc ouverte aux seuls
    rôles qui ont une action sur une étape « Terminée (à valider) » dans la table
    des transitions, c'est-à-dire au chef : le droit ne peut pas diverger du cycle.
    """
    return bool(actions_permises(StatutEtape.TERMINEE_A_VALIDER, acteur.role))
