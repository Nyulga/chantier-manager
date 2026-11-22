from decimal import Decimal

import pytest

from app.chantiers.domain.adresse import Adresse
from app.chantiers.domain.montant import DEVISE, Montant
from app.shared.domain.erreurs import ValeurInvalideError


@pytest.mark.parametrize("valeur", ["0", "0.00", "125000.50", "7", "9999999999.99"])
def test_un_montant_positif_ou_nul_au_centime_pres_est_accepte(valeur: str) -> None:
    montant = Montant(Decimal(valeur))

    assert montant.valeur == Decimal(valeur)


@pytest.mark.parametrize(
    "valeur", ["-0.01", "-100", "10.001", "NaN", "Infinity", "-Infinity", "10000000000", "1E+40"]
)
def test_un_montant_negatif_non_fini_trop_grand_ou_plus_precis_que_le_centime_est_refuse(
    valeur: str,
) -> None:
    with pytest.raises(ValeurInvalideError):
        Montant(Decimal(valeur))


@pytest.mark.parametrize(
    ("saisie", "attendu"), [("1E3", "1000.00"), ("125000.5", "125000.50"), ("0", "0.00")]
)
def test_un_montant_est_stocke_arrondi_au_centime(saisie: str, attendu: str) -> None:
    assert str(Montant(Decimal(saisie)).valeur) == attendu


def test_un_montant_est_exprime_en_euros() -> None:
    assert DEVISE == "EUR"


def test_une_adresse_complete_est_acceptee() -> None:
    adresse = Adresse(voie="1 place de la Gare", code_postal="13001", ville="Marseille")

    assert (adresse.voie, adresse.code_postal, adresse.ville) == (
        "1 place de la Gare",
        "13001",
        "Marseille",
    )


@pytest.mark.parametrize(
    ("voie", "code_postal", "ville"),
    [("", "13001", "Marseille"), ("1 place", "  ", "Marseille"), ("1 place", "13001", "\t")],
)
def test_une_adresse_avec_un_champ_vide_est_refusee(
    voie: str, code_postal: str, ville: str
) -> None:
    with pytest.raises(ValeurInvalideError):
        Adresse(voie=voie, code_postal=code_postal, ville=ville)
