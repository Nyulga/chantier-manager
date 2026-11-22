"""Cycle de vie d'une étape : statuts, actions et table déclarative des transitions.

Le cycle est décrit par une table plutôt que par des `if` : ajouter une transition
revient à ajouter une ligne (règle 00, principe ouvert/fermé), et la table sert à
la fois à appliquer une action et à calculer les actions permises affichées.
"""

from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum
from typing import Final

from app.shared.domain.acteur import Role
from app.shared.domain.erreurs import TransitionInterditeError, ValeurInvalideError


class StatutEtape(StrEnum):
    """Statut d'une étape, dans l'ordre du cycle : à faire, en cours, à valider, validée."""

    A_FAIRE = "a_faire"
    EN_COURS = "en_cours"
    TERMINEE_A_VALIDER = "terminee_a_valider"
    VALIDEE = "validee"


class ActionEtape(StrEnum):
    """Action qu'un acteur demande sur une étape pour la faire changer de statut."""

    DEMARRER = "demarrer"
    SIGNALER_TERMINEE = "signaler_terminee"
    VALIDER = "valider"
    REFUSER = "refuser"


@dataclass(frozen=True, slots=True)
class Transition:
    """Une ligne de la table : le statut d'arrivée et les rôles qui ont le droit d'agir.

    `commentaire_obligatoire` est porté par la transition, et non codé à part, pour
    que la règle du refus commenté reste lisible dans la table elle-même.
    """

    arrivee: StatutEtape
    roles: frozenset[Role]
    commentaire_obligatoire: bool = False


TOUS_LES_ROLES: Final = frozenset(Role)
CHEF_UNIQUEMENT: Final = frozenset({Role.CHEF})

# Table des transitions : (statut de départ, action) → transition (intent.md, §1).
# L'ouvrier fait avancer l'étape jusqu'à « Terminée (à valider) » ; seul un chef
# valide, ou refuse avec un commentaire qui explique ce qu'il faut reprendre.
TRANSITIONS: Final[Mapping[tuple[StatutEtape, ActionEtape], Transition]] = {
    (StatutEtape.A_FAIRE, ActionEtape.DEMARRER): Transition(StatutEtape.EN_COURS, TOUS_LES_ROLES),
    (StatutEtape.EN_COURS, ActionEtape.SIGNALER_TERMINEE): Transition(
        StatutEtape.TERMINEE_A_VALIDER, TOUS_LES_ROLES
    ),
    (StatutEtape.TERMINEE_A_VALIDER, ActionEtape.VALIDER): Transition(
        StatutEtape.VALIDEE, CHEF_UNIQUEMENT
    ),
    (StatutEtape.TERMINEE_A_VALIDER, ActionEtape.REFUSER): Transition(
        StatutEtape.EN_COURS, CHEF_UNIQUEMENT, commentaire_obligatoire=True
    ),
}


def trouver_transition(statut: StatutEtape, action: ActionEtape, role: Role) -> Transition:
    """Renvoie la transition que ce rôle peut effectuer, avec cette action, depuis ce statut.

    Un rôle non autorisé lève aussi `TransitionInterditeError`, et non `AccesRefuseError` :
    l'action n'existe pas pour lui dans cet état, ce que l'api traduit en 409.

    Lève :
        TransitionInterditeError : la combinaison est absente de la table, ou le rôle
            n'y figure pas.
    """
    transition = TRANSITIONS.get((statut, action))
    if transition is None or role not in transition.roles:
        raise TransitionInterditeError(
            "Cette action n'est pas possible sur l'étape dans son état actuel."
        )
    return transition


def actions_permises(statut: StatutEtape, role: Role) -> tuple[ActionEtape, ...]:
    """Liste, dans l'ordre de la table, les actions que ce rôle peut faire depuis ce statut.

    Le frontend affiche ces actions telles quelles : il n'a jamais à recalculer le
    cycle (règle 02, vues).
    """
    return tuple(
        action
        for (depart, action), transition in TRANSITIONS.items()
        if depart is statut and role in transition.roles
    )


def lire_action(nom: str) -> ActionEtape:
    """Convertit le nom reçu de l'extérieur en action du cycle.

    Lève :
        ValeurInvalideError : le nom ne correspond à aucune action.
    """
    try:
        return ActionEtape(nom)
    except ValueError:
        raise ValeurInvalideError("Action inconnue sur une étape.") from None
