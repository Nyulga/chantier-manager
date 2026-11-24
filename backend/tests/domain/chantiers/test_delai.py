"""Délai d'un chantier : jours restants avant l'échéance, ou jours de retard."""

from datetime import date, timedelta

import pytest
from hypothesis import given
from hypothesis import strategies as st

from app.chantiers.domain.delai import Delai, calculer_delai
from app.shared.domain.erreurs import ValeurInvalideError

ECHEANCE = date(2027, 3, 31)
ECART_MAX = 3650
# Des dates éloignées des bornes de `date`, pour que l'écart ne déborde jamais.
DATES = st.dates(min_value=date(2000, 1, 1), max_value=date(2100, 12, 31))


@pytest.mark.parametrize(
    ("aujourd_hui", "attendu"),
    [
        (date(2027, 3, 30), Delai(jours_restants=1, en_retard=False)),
        (date(2027, 3, 31), Delai(jours_restants=0, en_retard=False)),
        (date(2027, 4, 1), Delai(jours_restants=1, en_retard=True)),
        (date(2026, 12, 1), Delai(jours_restants=120, en_retard=False)),
        (date(2027, 4, 10), Delai(jours_restants=10, en_retard=True)),
    ],
    ids=["la-veille", "le-jour-meme", "le-lendemain", "longtemps-avant", "longtemps-apres"],
)
def test_le_delai_compte_les_jours_restants_ou_les_jours_de_retard(
    aujourd_hui: date, attendu: Delai
) -> None:
    assert calculer_delai(ECHEANCE, aujourd_hui) == attendu


@pytest.mark.parametrize(
    ("jours_restants", "en_retard"),
    [(-1, False), (-3, True), (0, True)],
    ids=["negatif", "negatif-en-retard", "en-retard-sans-jour-de-retard"],
)
def test_un_delai_incoherent_est_refuse(jours_restants: int, en_retard: bool) -> None:
    with pytest.raises(ValeurInvalideError):
        Delai(jours_restants=jours_restants, en_retard=en_retard)


@given(DATES, st.integers(min_value=0, max_value=ECART_MAX))
def test_avant_l_echeance_les_jours_restants_sont_l_ecart(aujourd_hui: date, ecart: int) -> None:
    echeance = aujourd_hui + timedelta(days=ecart)

    assert calculer_delai(echeance, aujourd_hui) == Delai(jours_restants=ecart, en_retard=False)


@given(DATES, st.integers(min_value=1, max_value=ECART_MAX))
def test_apres_l_echeance_les_jours_de_retard_sont_l_ecart(aujourd_hui: date, ecart: int) -> None:
    echeance = aujourd_hui - timedelta(days=ecart)

    assert calculer_delai(echeance, aujourd_hui) == Delai(jours_restants=ecart, en_retard=True)
