from uuid import UUID

from app.chantiers.application.ports import ResumeEtapes
from app.composition.resume_etapes import ResumeEtapesDepuisEtapes
from app.etapes.application import CalculerResumesEtapes
from app.etapes.domain.cycle import StatutEtape
from app.etapes.infrastructure.memoire.unit_of_work import MemoireUnitOfWorkEtapes
from tests.unitaires.etapes.fabriques import ID_CHANTIER, une_etape

CHANTIER_SANS_ETAPE = UUID(int=200)


def test_l_adaptateur_traduit_le_resume_d_etapes_dans_le_type_de_chantiers() -> None:
    uow = MemoireUnitOfWorkEtapes()
    uow.etapes.ajouter(une_etape(StatutEtape.VALIDEE, ordre=1))
    uow.etapes.ajouter(une_etape(StatutEtape.TERMINEE_A_VALIDER, ordre=2))
    adaptateur = ResumeEtapesDepuisEtapes(CalculerResumesEtapes(uow))

    resumes = adaptateur.executer([ID_CHANTIER, CHANTIER_SANS_ETAPE])

    assert resumes == {
        ID_CHANTIER: ResumeEtapes(avancement=50, validees=1, total=2, a_valider=1),
        CHANTIER_SANS_ETAPE: ResumeEtapes(avancement=0, validees=0, total=0, a_valider=0),
    }
