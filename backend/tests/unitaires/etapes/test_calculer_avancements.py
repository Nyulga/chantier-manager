from uuid import UUID

from app.etapes.domain.cycle import StatutEtape
from tests.unitaires.etapes.contexte import Contexte
from tests.unitaires.etapes.fabriques import ID_CHANTIER, une_etape

CHANTIER_SANS_ETAPE = UUID(int=200)
CHANTIER_NON_DEMANDE = UUID(int=300)


def test_l_avancement_est_calcule_pour_chaque_chantier_demande() -> None:
    contexte = Contexte()
    contexte.uow.etapes.ajouter(une_etape(StatutEtape.VALIDEE, ordre=1))
    contexte.uow.etapes.ajouter(une_etape(StatutEtape.EN_COURS, ordre=2))
    contexte.uow.etapes.ajouter(
        une_etape(StatutEtape.VALIDEE, ordre=1, chantier_id=CHANTIER_NON_DEMANDE)
    )

    avancements = contexte.calculer_avancements().executer([ID_CHANTIER, CHANTIER_SANS_ETAPE])

    assert avancements == {ID_CHANTIER: 50, CHANTIER_SANS_ETAPE: 0}


def test_sans_chantier_demande_le_resultat_est_vide() -> None:
    assert Contexte().calculer_avancements().executer([]) == {}
