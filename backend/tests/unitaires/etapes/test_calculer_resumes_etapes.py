"""Cas d'usage public `CalculerResumesEtapes` : un résumé par chantier demandé."""

from uuid import UUID

from app.etapes.application.vues import ResumeEtapesVue
from app.etapes.domain.cycle import StatutEtape
from tests.unitaires.etapes.contexte import Contexte
from tests.unitaires.etapes.fabriques import ID_CHANTIER, une_etape

CHANTIER_SANS_ETAPE = UUID(int=200)
CHANTIER_NON_DEMANDE = UUID(int=300)
RESUME_NUL = ResumeEtapesVue(avancement=0, validees=0, total=0, a_valider=0)


def test_le_resume_est_calcule_pour_chaque_chantier_demande() -> None:
    contexte = Contexte()
    contexte.uow.etapes.ajouter(une_etape(StatutEtape.VALIDEE, ordre=1))
    contexte.uow.etapes.ajouter(une_etape(StatutEtape.TERMINEE_A_VALIDER, ordre=2))
    contexte.uow.etapes.ajouter(une_etape(StatutEtape.EN_COURS, ordre=3))
    contexte.uow.etapes.ajouter(une_etape(StatutEtape.A_FAIRE, ordre=4))
    contexte.uow.etapes.ajouter(
        une_etape(StatutEtape.VALIDEE, ordre=1, chantier_id=CHANTIER_NON_DEMANDE)
    )

    resumes = contexte.calculer_resumes().executer([ID_CHANTIER, CHANTIER_SANS_ETAPE])

    assert resumes == {
        ID_CHANTIER: ResumeEtapesVue(avancement=25, validees=1, total=4, a_valider=1),
        CHANTIER_SANS_ETAPE: RESUME_NUL,
    }


def test_sans_chantier_demande_le_resultat_est_vide() -> None:
    assert Contexte().calculer_resumes().executer([]) == {}


def test_le_calcul_ne_valide_aucune_transaction() -> None:
    contexte = Contexte()

    contexte.calculer_resumes().executer([ID_CHANTIER])

    assert contexte.uow.validations == 0
