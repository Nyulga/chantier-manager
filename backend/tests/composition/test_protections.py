"""Assemblage des protections : le second limiteur (bloc IPv6 /48) a des seuils multipliés par 4."""

import pytest

from app.composition.parametres import Parametres
from app.composition.protections import creer_protections
from app.shared.application.limites_debit import (
    ECRITURES_PAR_FENETRE,
    FACTEUR_BLOC_IPV6_48,
    LECTURES_PAR_FENETRE,
)
from app.shared.application.ports import CategorieAcces, LimiteurDebit

CLE = "2001:db8:1::/48"
ECRITURES_REGLEES = 3
LECTURES_REGLEES = 7


def acces_permis_avant_le_premier_refus(limiteur: LimiteurDebit, categorie: CategorieAcces) -> int:
    """Compte les accès qu'un limiteur permet à une même clé avant de refuser."""
    permis = 0
    while limiteur.consommer(CLE, categorie) is None:
        permis += 1
    return permis


@pytest.mark.parametrize(
    ("categorie", "seuil_habituel"),
    [
        (CategorieAcces.ECRITURE, ECRITURES_PAR_FENETRE),
        (CategorieAcces.LECTURE, LECTURES_PAR_FENETRE),
    ],
)
def test_le_limiteur_du_bloc_48_a_les_seuils_par_defaut_multiplies_par_quatre(
    categorie: CategorieAcces, seuil_habituel: int
) -> None:
    protections = creer_protections(Parametres())

    permis = acces_permis_avant_le_premier_refus(protections.limiteur_bloc_48, categorie)

    assert permis == seuil_habituel * FACTEUR_BLOC_IPV6_48


def test_le_limiteur_du_bloc_48_suit_les_seuils_regles_dans_les_parametres() -> None:
    protections = creer_protections(
        Parametres(ecritures_par_minute=ECRITURES_REGLEES, lectures_par_minute=LECTURES_REGLEES)
    )

    ecritures = acces_permis_avant_le_premier_refus(
        protections.limiteur_bloc_48, CategorieAcces.ECRITURE
    )
    lectures = acces_permis_avant_le_premier_refus(
        protections.limiteur_bloc_48, CategorieAcces.LECTURE
    )

    assert ecritures == ECRITURES_REGLEES * FACTEUR_BLOC_IPV6_48
    assert lectures == LECTURES_REGLEES * FACTEUR_BLOC_IPV6_48


def test_le_limiteur_habituel_garde_les_seuils_des_parametres() -> None:
    protections = creer_protections(
        Parametres(ecritures_par_minute=ECRITURES_REGLEES, lectures_par_minute=LECTURES_REGLEES)
    )

    ecritures = acces_permis_avant_le_premier_refus(protections.limiteur, CategorieAcces.ECRITURE)

    assert ecritures == ECRITURES_REGLEES


def test_les_deux_limiteurs_ont_chacun_leur_propre_compte() -> None:
    protections = creer_protections(Parametres(ecritures_par_minute=1))
    protections.limiteur.consommer(CLE, CategorieAcces.ECRITURE)

    refus_habituel = protections.limiteur.consommer(CLE, CategorieAcces.ECRITURE)
    permis_du_bloc = protections.limiteur_bloc_48.consommer(CLE, CategorieAcces.ECRITURE)

    assert refus_habituel is not None
    assert permis_du_bloc is None
