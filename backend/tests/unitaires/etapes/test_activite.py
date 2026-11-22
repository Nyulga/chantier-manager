"""Limite du fil d'activité : un nombre d'entrées borné."""

import pytest

from app.etapes.domain.activite import (
    LIMITE_ACTIVITE_MAX,
    LIMITE_ACTIVITE_MIN,
    LIMITE_ACTIVITE_PAR_DEFAUT,
    LimiteActivite,
)
from app.shared.domain.erreurs import ValeurInvalideError


def test_les_bornes_de_la_limite_sont_1_et_50_avec_10_par_defaut() -> None:
    bornes = (LIMITE_ACTIVITE_MIN, LIMITE_ACTIVITE_MAX, LIMITE_ACTIVITE_PAR_DEFAUT)

    assert (bornes, LimiteActivite().valeur) == ((1, 50, 10), 10)


@pytest.mark.parametrize("valeur", [1, 10, 50])
def test_une_limite_dans_les_bornes_est_acceptee(valeur: int) -> None:
    assert LimiteActivite(valeur).valeur == valeur


@pytest.mark.parametrize("valeur", [0, -1, 51, 1000])
def test_une_limite_hors_des_bornes_est_refusee(valeur: int) -> None:
    with pytest.raises(ValeurInvalideError):
        LimiteActivite(valeur)
