"""Table des transitions du cycle d'une étape : exhaustive, immuable et lue par rôle.

Une action hors de la table est refusée de deux façons, selon le rôle : si ce rôle n'a
jamais droit à l'action, depuis aucun statut, c'est un refus de droit ; sinon, c'est
une transition impossible dans l'état actuel.
"""

from collections.abc import MutableMapping
from itertools import product

import pytest

from app.etapes.domain.cycle import (
    TRANSITIONS,
    ActionEtape,
    StatutEtape,
    actions_permises,
    lire_action,
    mene_a_un_statut_final,
    trouver_transition,
)
from app.shared.domain.acteur import Role
from app.shared.domain.erreurs import (
    AccesRefuseError,
    TransitionInterditeError,
    ValeurInvalideError,
)

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
# Les actions qu'un rôle ne peut faire depuis aucun statut : l'ouvrier ne valide ni ne
# refuse jamais. Écrites ici, elles aussi, indépendamment du code testé.
JAMAIS_PERMISES = {
    (ActionEtape.VALIDER, Role.OUVRIER),
    (ActionEtape.REFUSER, Role.OUVRIER),
}
HORS_TABLE = [cas for cas in product(StatutEtape, ActionEtape, Role) if cas not in AUTORISEES]
REFUS_DE_DROIT = [(s, a, r) for s, a, r in HORS_TABLE if (a, r) in JAMAIS_PERMISES]
INTERDITES = [(s, a, r) for s, a, r in HORS_TABLE if (a, r) not in JAMAIS_PERMISES]


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


@pytest.mark.parametrize(("depart", "action", "role"), REFUS_DE_DROIT)
def test_une_action_jamais_permise_au_role_est_un_refus_de_droit(
    depart: StatutEtape, action: ActionEtape, role: Role
) -> None:
    with pytest.raises(AccesRefuseError) as erreur:
        trouver_transition(depart, action, role)

    assert str(erreur.value) == "Ton profil ne permet pas cette action sur une étape."


def test_la_matrice_couvre_chaque_cas_hors_table_une_seule_fois() -> None:
    nombre_de_cas = len(StatutEtape) * len(ActionEtape) * len(Role)

    assert len(AUTORISEES) + len(INTERDITES) + len(REFUS_DE_DROIT) == nombre_de_cas
    assert len(REFUS_DE_DROIT) == len(StatutEtape) * len(JAMAIS_PERMISES)


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


# Seule la validation mène à « Validée », d'où ne part aucune transition : c'est la
# seule action qui ne peut pas servir à faire tourner le cycle en boucle.
@pytest.mark.parametrize(
    ("action", "finale"),
    [
        (ActionEtape.DEMARRER, False),
        (ActionEtape.SIGNALER_TERMINEE, False),
        (ActionEtape.VALIDER, True),
        (ActionEtape.REFUSER, False),
    ],
)
def test_seule_la_validation_mene_a_un_statut_final(action: ActionEtape, finale: bool) -> None:
    assert mene_a_un_statut_final(action) is finale
