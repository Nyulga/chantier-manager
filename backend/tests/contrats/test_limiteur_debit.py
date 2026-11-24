"""Contrat du port `LimiteurDebit`, joué sur toutes ses implémentations.

Il n'y en a qu'une pour l'instant, en mémoire (ADR 0015 : un seul processus API).
Pour en brancher une autre (Redis, base de données) le jour où l'API tournera sur
plusieurs processus, il suffit d'ajouter son nom dans `IMPLEMENTATIONS` et sa
construction dans la fixture `limiteur` : les mêmes tests s'appliquent, avec les
mêmes seuils et la même fenêtre, sans toucher à un seul test.
"""

from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta

import pytest

from app.shared.application.ports import CategorieAcces, LimiteurDebit
from app.shared.infrastructure.limiteur_debit_memoire import MemoireLimiteurDebit
from app.shared.infrastructure.memoire.horloge_avancable import HorlogeAvancable

IMPLEMENTATIONS = ["memoire"]
FENETRE = timedelta(seconds=60)
SEUIL_ECRITURES = 2
SEUIL_LECTURES = 3
ADRESSE = "203.0.113.7"
AUTRE_ADRESSE = "203.0.113.8"
ECRITURE = CategorieAcces.ECRITURE
LECTURE = CategorieAcces.LECTURE
# Un grand nombre de tentatives simultanées, pour un seuil bien plus petit.
TENTATIVES_SIMULTANEES = 400
SEUIL_SIMULTANE = 50
FILS_D_EXECUTION = 8


@pytest.fixture(params=IMPLEMENTATIONS)
def fabrique(
    request: pytest.FixtureRequest, horloge_avancable: HorlogeAvancable
) -> Callable[[int], LimiteurDebit]:
    """Construit un limiteur de la fenêtre du contrat, pour le seuil d'écritures donné.

    Pour brancher une autre implémentation, ajouter un `case` selon `request.param`.
    """
    return lambda seuil_ecritures: MemoireLimiteurDebit(
        horloge_avancable,
        {ECRITURE: seuil_ecritures, LECTURE: SEUIL_LECTURES},
        FENETRE,
    )


@pytest.fixture
def limiteur(fabrique: Callable[[int], LimiteurDebit]) -> LimiteurDebit:
    """Limiteur : 2 écritures et 3 lectures par fenêtre de 60 secondes."""
    return fabrique(SEUIL_ECRITURES)


def epuiser_les_ecritures(limiteur: LimiteurDebit, adresse: str = ADRESSE) -> None:
    for _ in range(SEUIL_ECRITURES):
        assert limiteur.consommer(adresse, ECRITURE) is None


def test_les_acces_sous_le_seuil_sont_permis(limiteur: LimiteurDebit) -> None:
    resultats = [limiteur.consommer(ADRESSE, ECRITURE) for _ in range(SEUIL_ECRITURES)]

    assert resultats == [None] * SEUIL_ECRITURES


def test_l_acces_qui_depasse_le_seuil_est_refuse_avec_un_delai(limiteur: LimiteurDebit) -> None:
    epuiser_les_ecritures(limiteur)

    delai = limiteur.consommer(ADRESSE, ECRITURE)

    assert delai == int(FENETRE.total_seconds())


@pytest.mark.parametrize(
    ("ecoule", "delai_attendu"),
    [
        (timedelta(seconds=30), 30),
        (timedelta(seconds=12, milliseconds=500), 48),
        (timedelta(seconds=59), 1),
        (timedelta(seconds=59, microseconds=999_999), 1),
    ],
    ids=["entier", "arrondi-vers-le-haut", "une-seconde", "jamais-zero"],
)
def test_le_delai_est_arrondi_vers_le_haut_et_vaut_au_moins_une_seconde(
    limiteur: LimiteurDebit,
    horloge_avancable: HorlogeAvancable,
    ecoule: timedelta,
    delai_attendu: int,
) -> None:
    epuiser_les_ecritures(limiteur)
    horloge_avancable.avancer(ecoule)

    delai = limiteur.consommer(ADRESSE, ECRITURE)

    assert delai == delai_attendu


def test_l_acces_est_permis_de_nouveau_une_fois_le_delai_ecoule(
    limiteur: LimiteurDebit, horloge_avancable: HorlogeAvancable
) -> None:
    epuiser_les_ecritures(limiteur)
    horloge_avancable.avancer(timedelta(seconds=12, milliseconds=500))
    delai = limiteur.consommer(ADRESSE, ECRITURE)
    assert delai is not None

    horloge_avancable.avancer(timedelta(seconds=delai))

    assert limiteur.consommer(ADRESSE, ECRITURE) is None


def test_l_acces_reste_refuse_un_instant_avant_la_fin_du_delai(
    limiteur: LimiteurDebit, horloge_avancable: HorlogeAvancable
) -> None:
    epuiser_les_ecritures(limiteur)

    horloge_avancable.avancer(FENETRE - timedelta(microseconds=1))

    assert limiteur.consommer(ADRESSE, ECRITURE) == 1


def test_les_acces_refuses_ne_consomment_rien(
    limiteur: LimiteurDebit, horloge_avancable: HorlogeAvancable
) -> None:
    epuiser_les_ecritures(limiteur)
    horloge_avancable.avancer(timedelta(seconds=10))
    delais = [limiteur.consommer(ADRESSE, ECRITURE) for _ in range(5)]
    horloge_avancable.avancer(timedelta(seconds=50))

    # Si les refus comptaient, ils tiendraient encore la fenêtre et refuseraient cet accès.
    assert set(delais) == {50}
    assert limiteur.consommer(ADRESSE, ECRITURE) is None


def test_la_fenetre_glisse_au_lieu_de_repartir_de_zero(
    limiteur: LimiteurDebit, horloge_avancable: HorlogeAvancable
) -> None:
    limiteur.consommer(ADRESSE, ECRITURE)
    horloge_avancable.avancer(timedelta(seconds=30))
    limiteur.consommer(ADRESSE, ECRITURE)
    horloge_avancable.avancer(timedelta(seconds=30))

    # Le premier accès a 60 secondes : il sort de la fenêtre, pas le second (30 secondes).
    premier = limiteur.consommer(ADRESSE, ECRITURE)
    second = limiteur.consommer(ADRESSE, ECRITURE)

    assert (premier, second) == (None, 30)


def test_chaque_adresse_a_son_propre_compteur(limiteur: LimiteurDebit) -> None:
    epuiser_les_ecritures(limiteur)

    assert limiteur.consommer(AUTRE_ADRESSE, ECRITURE) is None


def test_chaque_categorie_a_son_propre_compteur(limiteur: LimiteurDebit) -> None:
    epuiser_les_ecritures(limiteur)

    assert limiteur.consommer(ADRESSE, LECTURE) is None


def test_epuiser_les_lectures_laisse_les_ecritures_permises(limiteur: LimiteurDebit) -> None:
    resultats = [limiteur.consommer(ADRESSE, LECTURE) for _ in range(SEUIL_LECTURES + 1)]

    assert resultats[:SEUIL_LECTURES] == [None] * SEUIL_LECTURES
    assert resultats[SEUIL_LECTURES] == int(FENETRE.total_seconds())
    assert limiteur.consommer(ADRESSE, ECRITURE) is None


def test_des_appels_simultanes_ne_depassent_jamais_le_seuil(
    fabrique: Callable[[int], LimiteurDebit],
) -> None:
    limiteur = fabrique(SEUIL_SIMULTANE)

    with ThreadPoolExecutor(max_workers=FILS_D_EXECUTION) as fils:
        resultats = list(
            fils.map(
                lambda _: limiteur.consommer(ADRESSE, ECRITURE),
                range(TENTATIVES_SIMULTANEES),
            )
        )

    assert resultats.count(None) == SEUIL_SIMULTANE
