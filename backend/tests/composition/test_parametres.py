"""Paramètres de l'application, lus une seule fois par la composition root."""

import pytest

from app.composition.parametres import Parametres

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
