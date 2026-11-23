"""Table des transitions du cycle d'une étape : exhaustive, immuable et lue par rôle."""

from collections.abc import MutableMapping
from itertools import product

import pytest

from app.etapes.domain.cycle import (
    TRANSITIONS,
    ActionEtape,
    StatutEtape,
    actions_permises,
    lire_action,
    trouver_transition,
)
from app.shared.domain.acteur import Role
from app.shared.domain.erreurs import TransitionInterditeError, ValeurInvalideError

A_FAIRE = StatutEtape.A_FAIRE
EN_COURS = StatutEtape.EN_COURS
TERMINEE = StatutEtape.TERMINEE_A_VALIDER
VALIDEE = StatutEtape.VALIDEE

# Les seules transitions autorisées, écrites ici indépendamment du code testé :
# (statut de départ, action, rôle) → statut d'arrivée.
AUTORISEES = {
    (A_FAIRE, ActionEtape.DEMARRER, Role.CHEF): EN_COURS,
    (A_FAIRE, ActionEtape.DEMARRER, Role.OUVRIER): EN_COURS,
    (EN_COURS, ActionEtape.SIGNALER_TERMINEE, Role.CHEF): TERMINEE,
    (EN_COURS, ActionEtape.SIGNALER_TERMINEE, Role.OUVRIER): TERMINEE,
    (TERMINEE, ActionEtape.VALIDER, Role.CHEF): VALIDEE,
    (TERMINEE, ActionEtape.REFUSER, Role.CHEF): EN_COURS,
}
INTERDITES = [cas for cas in product(StatutEtape, ActionEtape, Role) if cas not in AUTORISEES]


def test_la_table_des_transitions_ne_peut_pas_etre_modifiee() -> None:
    table: object = TRANSITIONS

    assert not isinstance(table, MutableMapping)


@pytest.mark.parametrize(("depart", "action", "role"), list(AUTORISEES))
def test_transition_autorisee(depart: StatutEtape, action: ActionEtape, role: Role) -> None:
    transition = trouver_transition(depart, action, role)

    assert transition.arrivee is AUTORISEES[(depart, action, role)]


@pytest.mark.parametrize(("depart", "action", "role"), INTERDITES)
def test_transition_interdite(depart: StatutEtape, action: ActionEtape, role: Role) -> None:
    with pytest.raises(TransitionInterditeError):
        trouver_transition(depart, action, role)


@pytest.mark.parametrize(
    ("action", "obligatoire"),
    [
        (ActionEtape.DEMARRER, False),
        (ActionEtape.SIGNALER_TERMINEE, False),
        (ActionEtape.VALIDER, False),
        (ActionEtape.REFUSER, True),
    ],
)
def test_seul_le_refus_exige_un_commentaire(action: ActionEtape, obligatoire: bool) -> None:
    depart = {
        ActionEtape.DEMARRER: A_FAIRE,
        ActionEtape.SIGNALER_TERMINEE: EN_COURS,
        ActionEtape.VALIDER: TERMINEE,
        ActionEtape.REFUSER: TERMINEE,
    }[action]

    transition = trouver_transition(depart, action, Role.CHEF)

    assert transition.commentaire_obligatoire is obligatoire


@pytest.mark.parametrize(
    ("statut", "role", "attendues"),
    [
        (A_FAIRE, Role.CHEF, (ActionEtape.DEMARRER,)),
        (A_FAIRE, Role.OUVRIER, (ActionEtape.DEMARRER,)),
        (EN_COURS, Role.CHEF, (ActionEtape.SIGNALER_TERMINEE,)),
        (EN_COURS, Role.OUVRIER, (ActionEtape.SIGNALER_TERMINEE,)),
        (TERMINEE, Role.CHEF, (ActionEtape.VALIDER, ActionEtape.REFUSER)),
        (TERMINEE, Role.OUVRIER, ()),
        (VALIDEE, Role.CHEF, ()),
        (VALIDEE, Role.OUVRIER, ()),
    ],
)
def test_actions_permises_selon_le_statut_et_le_role(
    statut: StatutEtape, role: Role, attendues: tuple[ActionEtape, ...]
) -> None:
    assert actions_permises(statut, role) == attendues


@pytest.mark.parametrize("action", list(ActionEtape))
def test_lire_une_action_connue(action: ActionEtape) -> None:
    assert lire_action(action.value) is action


@pytest.mark.parametrize("nom", ["", "supprimer", "VALIDER"])
def test_lire_une_action_inconnue_est_refuse(nom: str) -> None:
    with pytest.raises(ValeurInvalideError):
        lire_action(nom)


def test_une_action_inconnue_designe_le_champ_action() -> None:
    with pytest.raises(ValeurInvalideError) as erreur:
        lire_action("supprimer")

    assert erreur.value.champ == "action"
