"""Politiques d'accès de chantiers : matrice des rôles et des actions."""

from collections.abc import Callable

import pytest

from app.chantiers.domain.politiques import (
    peut_ajouter_etape,
    peut_creer_chantier,
    peut_voir_budget,
)
from app.shared.domain.acteur import Acteur, Role

Politique = Callable[[Acteur], bool]

# Matrice des rôles et des actions : dans le squelette, il n'y a pas encore d'affectation,
# donc la troisième dimension (affecté ou non) n'existe pas.
MATRICE: list[tuple[Politique, Role, bool]] = [
    (peut_creer_chantier, Role.CHEF, True),
    (peut_creer_chantier, Role.OUVRIER, False),
    (peut_voir_budget, Role.CHEF, True),
    (peut_voir_budget, Role.OUVRIER, False),
    (peut_ajouter_etape, Role.CHEF, True),
    (peut_ajouter_etape, Role.OUVRIER, False),
]


@pytest.mark.parametrize(("politique", "role", "attendu"), MATRICE)
def test_matrice_des_droits_sur_les_chantiers(
    politique: Politique, role: Role, attendu: bool
) -> None:
    assert politique(Acteur(role)) is attendu
