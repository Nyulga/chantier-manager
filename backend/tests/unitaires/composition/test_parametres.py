import pytest

from app.composition.parametres import Parametres

URL_PRODUCTION = "sqlite:////donnees/chantier.db"


def test_l_url_de_la_base_est_lue_dans_chantier_url_base(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CHANTIER_URL_BASE", URL_PRODUCTION)

    assert Parametres().url_base == URL_PRODUCTION
