"""Politiques d'accès du module étapes : des fonctions pures qui ne lèvent rien.

Dans le squelette, il n'y a pas encore d'affectation : les droits ne dépendent que
du rôle. En phase 2, ils dépendront aussi des chantiers de l'acteur (intent.md, §1).
"""

from app.etapes.domain.cycle import TRANSITIONS, StatutEtape, actions_permises
from app.shared.domain.acteur import Acteur


def peut_lister_etapes_a_valider(acteur: Acteur) -> bool:
    """Dit si l'acteur peut consulter la file des étapes à valider.

    Cette file ne sert qu'à valider ou à refuser. Elle est donc ouverte aux seuls
    rôles qui ont une action sur une étape « Terminée (à valider) » dans la table
    des transitions, c'est-à-dire au chef : le droit ne peut pas diverger du cycle.
    """
    return bool(actions_permises(StatutEtape.TERMINEE_A_VALIDER, acteur.role))


def peut_consulter_activite(acteur: Acteur) -> bool:
    """Dit si l'acteur peut consulter le fil d'activité des étapes.

    Le fil retrace les transitions du cycle : il est ouvert à tout rôle qui peut en
    effectuer au moins une dans la table, pour suivre ce qui avance. Dans le
    squelette, c'est le cas du chef comme de l'ouvrier, et la politique est donc
    vraie pour les deux : faute d'affectation, chacun voit tous les chantiers
    (docs/plan/squelette.md), donc toute leur activité. En phase 2, le fil sera
    filtré par chantier : l'acteur n'y verra que l'activité des chantiers auxquels
    il est rattaché (intent.md, §1, cloisonnement).
    """
    return any(acteur.role in transition.roles for transition in TRANSITIONS.values())
