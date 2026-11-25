"""Garde des plafonds de volume : refuse une création qui dépasserait le plafond."""

import pytest

from app.shared.application.erreurs import PlafondAtteintError
from app.shared.application.plafond import exiger_place_sous_le_plafond
from app.shared.domain.erreurs import ErreurMetierError

PLAFOND = 3
MESSAGE = "La limite de 3 éléments est atteinte."


@pytest.mark.parametrize("existants", [0, PLAFOND - 1])
def test_une_creation_sous_le_plafond_est_permise(existants: int) -> None:
    exiger_place_sous_le_plafond(existants, PLAFOND, MESSAGE)


@pytest.mark.parametrize("existants", [PLAFOND, PLAFOND + 1])
def test_une_creation_au_plafond_ou_au_dela_est_refusee_avec_le_message(existants: int) -> None:
    with pytest.raises(PlafondAtteintError) as erreur:
        exiger_place_sous_le_plafond(existants, PLAFOND, MESSAGE)

    assert str(erreur.value) == MESSAGE


def test_un_plafond_atteint_est_une_erreur_metier_affichable() -> None:
    assert issubclass(PlafondAtteintError, ErreurMetierError)
