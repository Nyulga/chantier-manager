"""Paramètres de l'application, lus une seule fois par la composition root."""

import pytest
from pydantic import ValidationError

from app.composition.parametres import Parametres
from app.shared.application.limites_debit import ECRITURES_PAR_FENETRE, LECTURES_PAR_FENETRE

URL_PRODUCTION = "sqlite:////donnees/chantier.db"
UN_KIBIOCTET = 1024


def test_l_url_de_la_base_est_lue_dans_chantier_url_base(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CHANTIER_URL_BASE", URL_PRODUCTION)

    assert Parametres().url_base == URL_PRODUCTION


def test_la_documentation_de_l_api_n_est_pas_exposee_par_defaut() -> None:
    assert Parametres().documentation_exposee is False


def test_la_documentation_est_exposee_par_chantier_documentation_exposee(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("CHANTIER_DOCUMENTATION_EXPOSEE", "true")

    assert Parametres().documentation_exposee is True


def test_seuls_les_hotes_locaux_sont_acceptes_par_defaut() -> None:
    assert Parametres().hotes_acceptes == ["localhost", "127.0.0.1"]


def test_les_hotes_acceptes_sont_lus_dans_chantier_hotes_acceptes(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("CHANTIER_HOTES_ACCEPTES", '["demo.example.org", "127.0.0.1"]')

    assert Parametres().hotes_acceptes == ["demo.example.org", "127.0.0.1"]


def test_le_corps_d_une_requete_est_limite_a_64_kio_par_defaut() -> None:
    assert Parametres().taille_max_corps == 64 * UN_KIBIOCTET


def test_la_taille_maximale_du_corps_est_lue_dans_chantier_taille_max_corps(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("CHANTIER_TAILLE_MAX_CORPS", str(UN_KIBIOCTET))

    assert Parametres().taille_max_corps == UN_KIBIOCTET


def test_les_seuils_de_debit_par_defaut_sont_ceux_decides_par_le_proprietaire() -> None:
    parametres = Parametres()

    assert parametres.ecritures_par_minute == ECRITURES_PAR_FENETRE
    assert parametres.lectures_par_minute == LECTURES_PAR_FENETRE


def test_les_seuils_de_debit_sont_lus_dans_l_environnement(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("CHANTIER_ECRITURES_PAR_MINUTE", "5000")
    monkeypatch.setenv("CHANTIER_LECTURES_PAR_MINUTE", "6000")

    parametres = Parametres()

    assert (parametres.ecritures_par_minute, parametres.lectures_par_minute) == (5000, 6000)


@pytest.mark.parametrize("variable", ["ecritures_par_minute", "lectures_par_minute"])
def test_un_seuil_de_debit_nul_est_refuse(variable: str) -> None:
    # Un seuil à zéro couperait toute l'API : mieux vaut refuser la configuration au démarrage.
    with pytest.raises(ValidationError):
        Parametres.model_validate({variable: 0})
