from collections.abc import Callable

import pytest

from app.etapes.domain.politiques import peut_consulter_activite, peut_lister_etapes_a_valider
from app.shared.domain.acteur import Acteur, Role

Politique = Callable[[Acteur], bool]

# Matrice des rôles et des actions : dans le squelette, il n'y a pas encore d'affectation,
# donc la troisième dimension (affecté ou non) n'existe pas.
MATRICE: list[tuple[Politique, Role, bool]] = [
    (peut_lister_etapes_a_valider, Role.CHEF, True),
    (peut_lister_etapes_a_valider, Role.OUVRIER, False),
    (peut_consulter_activite, Role.CHEF, True),
    (peut_consulter_activite, Role.OUVRIER, True),
]


@pytest.mark.parametrize(("politique", "role", "attendu"), MATRICE)
def test_matrice_des_droits_sur_les_etapes(politique: Politique, role: Role, attendu: bool) -> None:
    assert politique(Acteur(role)) is attendu
