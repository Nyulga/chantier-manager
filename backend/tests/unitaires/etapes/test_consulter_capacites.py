"""Cas d'usage `ConsulterCapacites` : ce que l'acteur peut faire, selon son rôle.

Les capacités viennent des politiques du domaine de chaque module ; la matrice
ci-dessous les écrit indépendamment du code testé.
"""

import pytest

from app.etapes.application.vues import CapacitesVue
from app.shared.domain.acteur import Acteur, Role
from tests.unitaires.etapes.contexte import Contexte

MATRICE = [
    (Role.CHEF, CapacitesVue("chef", peut_creer_chantier=True, peut_lister_etapes_a_valider=True)),
    (
        Role.OUVRIER,
        CapacitesVue("ouvrier", peut_creer_chantier=False, peut_lister_etapes_a_valider=False),
    ),
]


@pytest.mark.parametrize(("role", "attendues"), MATRICE)
def test_matrice_des_capacites_par_role(role: Role, attendues: CapacitesVue) -> None:
    contexte = Contexte()

    capacites = contexte.consulter_capacites().executer(Acteur(role))

    assert capacites == attendues


def test_chaque_role_a_sa_ligne_dans_la_matrice() -> None:
    assert {role for role, _ in MATRICE} == set(Role)


def test_consulter_ses_capacites_n_ouvre_aucune_transaction() -> None:
    contexte = Contexte()

    contexte.consulter_capacites().executer(Acteur(Role.CHEF))

    assert (contexte.uow.validations, contexte.chantiers.validations) == (0, 0)
