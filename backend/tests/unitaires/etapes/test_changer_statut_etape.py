"""Cas d'usage `ChangerStatutEtape` : transitions, refus, verrou de version et annulation."""

from uuid import UUID

import pytest

from app.etapes.application.changer_statut_etape import ChangementStatut
from app.etapes.domain.cycle import StatutEtape
from app.etapes.domain.etape import HistoriqueEtape
from app.shared.domain.acteur import Acteur, Role
from app.shared.domain.erreurs import (
    ConflitVersionError,
    NonTrouveError,
    TransitionInterditeError,
    ValeurInvalideError,
)
from tests.unitaires.etapes.contexte import Contexte
from tests.unitaires.etapes.fabriques import INSTANT, id_etape, une_etape

CHEF = Acteur(Role.CHEF)
OUVRIER = Acteur(Role.OUVRIER)
ETAPE = id_etape(1)


def un_contexte(statut: StatutEtape) -> Contexte:
    contexte = Contexte()
    contexte.uow.etapes.ajouter(une_etape(statut))
    return contexte


def test_un_ouvrier_demarre_une_etape_et_la_transition_est_tracee() -> None:
    contexte = un_contexte(StatutEtape.A_FAIRE)

    vue = contexte.changer_statut().executer(ChangementStatut(ETAPE, "demarrer"), OUVRIER)

    assert (vue.statut, vue.version, vue.actions_permises) == (
        "en_cours",
        2,
        ("signaler_terminee",),
    )
    assert contexte.uow.etapes.obtenir(ETAPE).historique == [
        HistoriqueEtape(Role.OUVRIER, StatutEtape.A_FAIRE, StatutEtape.EN_COURS, INSTANT, None)
    ]
    assert contexte.uow.validations == 1


def test_un_chef_valide_une_etape_terminee() -> None:
    contexte = un_contexte(StatutEtape.TERMINEE_A_VALIDER)

    vue = contexte.changer_statut().executer(ChangementStatut(ETAPE, "valider"), CHEF)

    assert (vue.statut, vue.actions_permises) == ("validee", ())


def test_un_chef_refuse_une_etape_avec_un_commentaire() -> None:
    contexte = un_contexte(StatutEtape.TERMINEE_A_VALIDER)
    commande = ChangementStatut(ETAPE, "refuser", "Joints à reprendre.")

    vue = contexte.changer_statut().executer(commande, CHEF)

    assert vue.statut == "en_cours"
    assert contexte.uow.etapes.obtenir(ETAPE).historique[-1].commentaire == "Joints à reprendre."


def test_une_version_attendue_a_jour_laisse_passer_la_transition() -> None:
    contexte = un_contexte(StatutEtape.TERMINEE_A_VALIDER)

    vue = contexte.changer_statut().executer(
        ChangementStatut(ETAPE, "valider", version_attendue=1), CHEF
    )

    assert (vue.statut, vue.version, contexte.uow.validations) == ("validee", 2, 1)


def test_une_seconde_action_sur_la_version_deja_modifiee_est_rejetee() -> None:
    contexte = un_contexte(StatutEtape.TERMINEE_A_VALIDER)
    cas_usage = contexte.changer_statut()
    cas_usage.executer(ChangementStatut(ETAPE, "valider", version_attendue=1), CHEF)

    with pytest.raises(ConflitVersionError):
        cas_usage.executer(
            ChangementStatut(ETAPE, "refuser", "Trop tard.", version_attendue=1), CHEF
        )

    etape = contexte.uow.etapes.obtenir(ETAPE)
    assert (etape.statut, etape.version, len(etape.historique)) == (StatutEtape.VALIDEE, 2, 1)


@pytest.mark.parametrize(
    ("commande", "acteur", "erreur"),
    [
        (ChangementStatut(ETAPE, "valider"), OUVRIER, TransitionInterditeError),
        (ChangementStatut(ETAPE, "refuser", "Non conforme."), OUVRIER, TransitionInterditeError),
        (ChangementStatut(ETAPE, "demarrer"), CHEF, TransitionInterditeError),
        (ChangementStatut(ETAPE, "refuser"), CHEF, ValeurInvalideError),
        (ChangementStatut(ETAPE, "refuser", " "), CHEF, ValeurInvalideError),
        (ChangementStatut(ETAPE, "archiver"), CHEF, ValeurInvalideError),
        (ChangementStatut(UUID(int=999), "valider"), CHEF, NonTrouveError),
        (ChangementStatut(ETAPE, "valider", version_attendue=2), CHEF, ConflitVersionError),
        (ChangementStatut(ETAPE, "valider", version_attendue=0), CHEF, ConflitVersionError),
        # Une version périmée l'emporte sur une transition interdite : l'acteur a agi
        # sur un état qui n'existe plus, c'est ce qu'il doit apprendre en premier.
        (ChangementStatut(ETAPE, "demarrer", version_attendue=2), CHEF, ConflitVersionError),
    ],
)
def test_un_changement_refuse_ne_modifie_rien(
    commande: ChangementStatut, acteur: Acteur, erreur: type[Exception]
) -> None:
    contexte = un_contexte(StatutEtape.TERMINEE_A_VALIDER)

    with pytest.raises(erreur):
        contexte.changer_statut().executer(commande, acteur)

    etape = contexte.uow.etapes.obtenir(ETAPE)
    assert (etape.statut, etape.version, etape.historique, contexte.uow.validations) == (
        StatutEtape.TERMINEE_A_VALIDER,
        1,
        [],
        0,
    )
