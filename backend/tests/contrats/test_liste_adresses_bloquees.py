"""Contrat du port `ListeAdressesBloquees`, joué sur toutes ses implémentations.

Il n'y en a qu'une pour l'instant, en mémoire (ADR 0016 : un seul processus API).
Pour en brancher une autre (Redis, base de données) le jour où l'API tournera sur
plusieurs processus, il suffit d'ajouter son nom dans `IMPLEMENTATIONS` et sa
construction dans la fixture `liste` : les mêmes tests s'appliquent, avec la même
durée de blocage, sans toucher à un seul test.
"""

from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta

import pytest

from app.shared.application.ports import ListeAdressesBloquees
from app.shared.infrastructure.adresses_bloquees_memoire import MemoireListeAdressesBloquees
from app.shared.infrastructure.memoire.horloge_avancable import HorlogeAvancable

IMPLEMENTATIONS = ["memoire"]
DUREE = timedelta(minutes=10)
UNE_MICROSECONDE = timedelta(microseconds=1)
ADRESSE = "203.0.113.7"
AUTRE_ADRESSE = "203.0.113.8"
ADRESSES_SIMULTANEES = 400
FILS_D_EXECUTION = 8


@pytest.fixture(params=IMPLEMENTATIONS)
def liste(
    request: pytest.FixtureRequest, horloge_avancable: HorlogeAvancable
) -> ListeAdressesBloquees:
    """Liste dont le blocage dure 10 minutes.

    Pour brancher une autre implémentation, ajouter un `case` selon `request.param`.
    """
    return MemoireListeAdressesBloquees(horloge_avancable, DUREE)


def test_une_adresse_jamais_bloquee_ne_l_est_pas(liste: ListeAdressesBloquees) -> None:
    assert liste.est_bloquee(ADRESSE) is False


def test_une_adresse_bloquee_l_est(liste: ListeAdressesBloquees) -> None:
    liste.bloquer(ADRESSE)

    assert liste.est_bloquee(ADRESSE) is True


def test_bloquer_une_adresse_n_en_bloque_pas_une_autre(liste: ListeAdressesBloquees) -> None:
    liste.bloquer(ADRESSE)

    assert liste.est_bloquee(AUTRE_ADRESSE) is False


def test_l_adresse_reste_bloquee_un_instant_avant_la_fin_de_la_duree(
    liste: ListeAdressesBloquees, horloge_avancable: HorlogeAvancable
) -> None:
    liste.bloquer(ADRESSE)

    horloge_avancable.avancer(DUREE - UNE_MICROSECONDE)

    assert liste.est_bloquee(ADRESSE) is True


def test_l_adresse_n_est_plus_bloquee_quand_la_duree_est_ecoulee(
    liste: ListeAdressesBloquees, horloge_avancable: HorlogeAvancable
) -> None:
    liste.bloquer(ADRESSE)

    horloge_avancable.avancer(DUREE)

    assert liste.est_bloquee(ADRESSE) is False


def test_une_adresse_peut_etre_bloquee_de_nouveau_apres_l_expiration(
    liste: ListeAdressesBloquees, horloge_avancable: HorlogeAvancable
) -> None:
    liste.bloquer(ADRESSE)
    horloge_avancable.avancer(DUREE)

    liste.bloquer(ADRESSE)

    assert liste.est_bloquee(ADRESSE) is True


def test_rebloquer_une_adresse_fait_repartir_la_duree_de_zero(
    liste: ListeAdressesBloquees, horloge_avancable: HorlogeAvancable
) -> None:
    liste.bloquer(ADRESSE)
    horloge_avancable.avancer(DUREE / 2)
    liste.bloquer(ADRESSE)

    # Depuis le premier blocage, la durée est écoulée ; depuis le second, pas encore.
    horloge_avancable.avancer(DUREE / 2)
    encore_bloquee = liste.est_bloquee(ADRESSE)
    horloge_avancable.avancer(DUREE / 2)

    assert encore_bloquee is True
    assert liste.est_bloquee(ADRESSE) is False


def test_des_blocages_simultanes_sont_tous_retenus(liste: ListeAdressesBloquees) -> None:
    adresses = [f"198.51.100.{numero}" for numero in range(ADRESSES_SIMULTANEES)]

    with ThreadPoolExecutor(max_workers=FILS_D_EXECUTION) as fils:
        list(fils.map(liste.bloquer, adresses))

    assert all(liste.est_bloquee(adresse) for adresse in adresses)
