"""Bornes mémoire de la liste d'adresses bloquées en mémoire (le contrat est dans tests/contrats).

Ces tests portent sur ce qui est propre à cette implémentation : elle oublie les
blocages expirés et plafonne le nombre d'adresses retenues. Le seul moyen honnête de
voir qu'elle oublie est de compter ce qu'elle retient (`nombre_d_adresses_bloquees`) :
vu de l'extérieur, un blocage expiré oublié ou gardé se comporte de la même façon.
"""

from datetime import UTC, datetime, timedelta

from app.shared.infrastructure.adresses_bloquees_memoire import (
    ADRESSES_BLOQUEES_MAX,
    MemoireListeAdressesBloquees,
)
from app.shared.infrastructure.memoire.horloge_avancable import HorlogeAvancable

INSTANT = datetime(2026, 11, 22, 8, 30, tzinfo=UTC)
DUREE = timedelta(minutes=10)
ADRESSES = ("a", "b", "c")
ADRESSES_MAX_DU_TEST = 2


def une_liste(
    adresses_max: int = ADRESSES_BLOQUEES_MAX,
) -> tuple[MemoireListeAdressesBloquees, HorlogeAvancable]:
    horloge = HorlogeAvancable(INSTANT)
    return MemoireListeAdressesBloquees(horloge, DUREE, adresses_max), horloge


def test_les_blocages_expires_sont_oublies_a_la_lecture() -> None:
    liste, horloge = une_liste()
    for adresse in ADRESSES:
        liste.bloquer(adresse)
    horloge.avancer(DUREE)

    liste.est_bloquee("d")

    assert liste.nombre_d_adresses_bloquees() == 0


def test_les_blocages_expires_sont_oublies_a_l_ecriture() -> None:
    liste, horloge = une_liste()
    for adresse in ADRESSES:
        liste.bloquer(adresse)
    horloge.avancer(DUREE)

    liste.bloquer("d")

    assert liste.nombre_d_adresses_bloquees() == 1


def test_les_blocages_en_cours_sont_gardes() -> None:
    liste, horloge = une_liste()
    for adresse in ADRESSES:
        liste.bloquer(adresse)
    horloge.avancer(DUREE - timedelta(microseconds=1))

    liste.est_bloquee("d")

    assert liste.nombre_d_adresses_bloquees() == len(ADRESSES)


def test_au_dela_du_maximum_le_blocage_le_plus_ancien_est_evince() -> None:
    liste, _ = une_liste(adresses_max=ADRESSES_MAX_DU_TEST)
    for adresse in ADRESSES:
        liste.bloquer(adresse)

    assert [liste.est_bloquee(adresse) for adresse in ("a", "b", "c")] == [False, True, True]


def test_rebloquer_une_adresse_la_met_a_l_abri_de_l_eviction() -> None:
    liste, _ = une_liste(adresses_max=ADRESSES_MAX_DU_TEST)
    for adresse in ("a", "b", "a", "c"):
        liste.bloquer(adresse)

    assert [liste.est_bloquee(adresse) for adresse in ("a", "b", "c")] == [True, False, True]
