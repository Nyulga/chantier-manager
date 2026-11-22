"""Résumé des étapes d'un chantier : compteurs et avancement."""

import pytest

from app.etapes.domain.avancement import ResumeEtapes, resumer_etapes
from app.etapes.domain.cycle import StatutEtape
from app.shared.domain.erreurs import ValeurInvalideError
from tests.unitaires.etapes.fabriques import une_etape

A_FAIRE = StatutEtape.A_FAIRE
EN_COURS = StatutEtape.EN_COURS
TERMINEE = StatutEtape.TERMINEE_A_VALIDER
VALIDEE = StatutEtape.VALIDEE
# Une étape validée sur trois : un tiers, arrondi à l'entier inférieur.
UN_TIERS = 33


def test_sans_etape_le_resume_est_nul_et_l_avancement_vaut_zero() -> None:
    resume = resumer_etapes([])

    assert (resume, resume.avancement) == (ResumeEtapes(total=0, validees=0, a_valider=0), 0)


@pytest.mark.parametrize(
    ("statuts", "validees", "a_valider"),
    [
        ([A_FAIRE, EN_COURS], 0, 0),
        ([TERMINEE, VALIDEE, TERMINEE, A_FAIRE], 1, 2),
        ([VALIDEE, VALIDEE], 2, 0),
    ],
)
def test_le_resume_compte_les_etapes_validees_et_celles_a_valider(
    statuts: list[StatutEtape], validees: int, a_valider: int
) -> None:
    etapes = [une_etape(statut, ordre) for ordre, statut in enumerate(statuts, start=1)]

    resume = resumer_etapes(etapes)

    assert resume == ResumeEtapes(total=len(statuts), validees=validees, a_valider=a_valider)


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

    assert resumer_etapes(etapes).avancement == attendu


@pytest.mark.parametrize(
    ("total", "validees", "a_valider"),
    [(-1, 0, 0), (2, -1, 0), (2, 0, -1), (2, 2, 1), (3, 1, 3)],
    ids=[
        "total-negatif",
        "validees-negatif",
        "a-valider-negatif",
        "trop-validees",
        "trop-a-valider",
    ],
)
def test_un_resume_incoherent_est_refuse(total: int, validees: int, a_valider: int) -> None:
    with pytest.raises(ValeurInvalideError):
        ResumeEtapes(total=total, validees=validees, a_valider=a_valider)


def test_un_resume_dont_toutes_les_etapes_sont_comptees_est_accepte() -> None:
    resume = ResumeEtapes(total=3, validees=1, a_valider=2)

    assert resume.avancement == UN_TIERS
