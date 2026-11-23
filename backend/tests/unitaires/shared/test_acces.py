"""Garde d'accès commune : un refus de politique devient `AccesRefuseError`."""

import pytest

from app.shared.application.acces import exiger_acces
from app.shared.domain.erreurs import AccesRefuseError


def test_un_acces_autorise_ne_leve_rien() -> None:
    exiger_acces(autorise=True, message="Accès refusé.")


def test_un_acces_refuse_leve_acces_refuse_avec_son_message() -> None:
    with pytest.raises(AccesRefuseError, match=r"^Seul un chef\.$"):
        exiger_acces(autorise=False, message="Seul un chef.")
