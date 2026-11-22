import pytest

from app.etapes.domain.avancement import calculer_avancement
from app.etapes.domain.cycle import StatutEtape
from tests.unitaires.etapes.fabriques import une_etape

A_FAIRE = StatutEtape.A_FAIRE
EN_COURS = StatutEtape.EN_COURS
TERMINEE = StatutEtape.TERMINEE_A_VALIDER
VALIDEE = StatutEtape.VALIDEE


def test_sans_etape_l_avancement_est_nul() -> None:
    assert calculer_avancement([]) == 0


@pytest.mark.parametrize(
    ("statuts", "attendu"),
    [
        ([A_FAIRE, EN_COURS, TERMINEE], 0),
        ([VALIDEE, A_FAIRE], 50),
        ([VALIDEE, VALIDEE, TERMINEE], 66),
        ([VALIDEE, VALIDEE, VALIDEE, VALIDEE, VALIDEE, VALIDEE, VALIDEE, EN_COURS], 87),
        ([VALIDEE, VALIDEE], 100),
    ],
)
def test_l_avancement_compte_seulement_les_etapes_validees_arrondi_a_l_inferieur(
    statuts: list[StatutEtape], attendu: int
) -> None:
    etapes = [une_etape(statut, ordre) for ordre, statut in enumerate(statuts, start=1)]

    assert calculer_avancement(etapes) == attendu
