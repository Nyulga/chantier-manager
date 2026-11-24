"""Contrat du port `ChantierRepository` : joué sur le fake mémoire et sur SQL."""

from decimal import Decimal

import pytest

from app.chantiers.application.ports import UnitOfWorkChantiers
from app.chantiers.domain.chantier import Chantier
from app.chantiers.domain.montant import MONTANT_MAX, Montant
from app.shared.domain.erreurs import NonTrouveError
from tests.fabriques.chantiers import un_chantier


def enregistrer(uow: UnitOfWorkChantiers, *chantiers: Chantier) -> None:
    with uow:
        for chantier in chantiers:
            uow.chantiers.ajouter(chantier)
        uow.valider()


def test_un_chantier_valide_est_relu_identique_dans_une_autre_transaction(
    uow_chantiers: UnitOfWorkChantiers,
) -> None:
    chantier = un_chantier(1)
    enregistrer(uow_chantiers, chantier)

    with uow_chantiers:
        relu = uow_chantiers.chantiers.obtenir(chantier.id)

    assert relu == chantier


@pytest.mark.parametrize(
    "valeur", [Decimal("0"), Decimal("0.01"), Decimal("125000.50"), MONTANT_MAX]
)
def test_le_budget_est_relu_au_centime_pres_en_decimal(
    uow_chantiers: UnitOfWorkChantiers, valeur: Decimal
) -> None:
    chantier = un_chantier(1)
    chantier.budget = Montant(valeur)
    enregistrer(uow_chantiers, chantier)

    with uow_chantiers:
        relu = uow_chantiers.chantiers.obtenir(chantier.id)

    assert isinstance(relu.budget.valeur, Decimal)
    assert relu.budget.valeur == valeur


def test_un_chantier_inconnu_leve_non_trouve(uow_chantiers: UnitOfWorkChantiers) -> None:
    with uow_chantiers, pytest.raises(NonTrouveError):
        uow_chantiers.chantiers.obtenir(un_chantier(9).id)


def test_une_transaction_non_validee_n_enregistre_rien(uow_chantiers: UnitOfWorkChantiers) -> None:
    chantier = un_chantier(1)

    with uow_chantiers:
        uow_chantiers.chantiers.ajouter(chantier)
    with uow_chantiers:
        restant = uow_chantiers.chantiers.lister()

    assert restant == []


def test_les_chantiers_sont_listes_dans_l_ordre_de_leur_identifiant(
    uow_chantiers: UnitOfWorkChantiers,
) -> None:
    enregistrer(uow_chantiers, un_chantier(3), un_chantier(1), un_chantier(2))

    with uow_chantiers:
        identifiants = [chantier.id.int for chantier in uow_chantiers.chantiers.lister()]

    assert identifiants == [1, 2, 3]
