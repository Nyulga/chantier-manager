"""Bornes mémoire du limiteur de débit en mémoire (le contrat est dans tests/contrats).

Ces tests portent sur ce qui est propre à cette implémentation : elle oublie les
adresses expirées et plafonne le nombre de clés suivies. Le seul moyen honnête de
voir qu'elle oublie est de compter ce qu'elle retient (`nombre_de_cles_suivies`) :
vu de l'extérieur, une clé expirée oubliée ou gardée se comporte de la même façon.
"""

from datetime import UTC, datetime, timedelta

from app.shared.application.ports import CategorieAcces
from app.shared.infrastructure.limiteur_debit_memoire import (
    CLES_SUIVIES_MAX,
    MemoireLimiteurDebit,
)
from app.shared.infrastructure.memoire.horloge_avancable import HorlogeAvancable

INSTANT = datetime(2026, 11, 22, 8, 30, tzinfo=UTC)
FENETRE = timedelta(seconds=60)
ADRESSES = ("a", "b", "c")
CLES_MAX_DU_TEST = 2
ECRITURE = CategorieAcces.ECRITURE
LECTURE = CategorieAcces.LECTURE


def un_limiteur(
    seuil_ecritures: int = 1, cles_max: int = CLES_SUIVIES_MAX
) -> tuple[MemoireLimiteurDebit, HorlogeAvancable]:
    horloge = HorlogeAvancable(INSTANT)
    return MemoireLimiteurDebit(
        horloge, {ECRITURE: seuil_ecritures, LECTURE: 1}, FENETRE, cles_max
    ), horloge


def test_les_adresses_expirees_sont_oubliees() -> None:
    limiteur, horloge = un_limiteur()
    for adresse in ADRESSES:
        limiteur.consommer(adresse, ECRITURE)
    horloge.avancer(FENETRE)

    limiteur.consommer("d", ECRITURE)

    assert limiteur.nombre_de_cles_suivies() == 1


def test_les_adresses_encore_dans_la_fenetre_sont_gardees() -> None:
    limiteur, horloge = un_limiteur()
    for adresse in ADRESSES:
        limiteur.consommer(adresse, ECRITURE)
    horloge.avancer(FENETRE - timedelta(microseconds=1))

    limiteur.consommer("d", ECRITURE)

    assert limiteur.nombre_de_cles_suivies() == len(ADRESSES) + 1


def test_une_adresse_compte_une_cle_par_categorie() -> None:
    limiteur, _ = un_limiteur()

    limiteur.consommer("a", ECRITURE)
    limiteur.consommer("a", LECTURE)

    assert limiteur.nombre_de_cles_suivies() == len(CategorieAcces)


def test_au_dela_du_maximum_la_cle_la_plus_ancienne_est_evincee() -> None:
    limiteur, _ = un_limiteur(cles_max=CLES_MAX_DU_TEST)
    for adresse in ADRESSES:
        limiteur.consommer(adresse, ECRITURE)

    # « b » est toujours comptée (refusée), « a » a été oubliée (permise de nouveau).
    assert limiteur.consommer("b", ECRITURE) is not None
    assert limiteur.consommer("a", ECRITURE) is None
    assert limiteur.nombre_de_cles_suivies() == CLES_MAX_DU_TEST


def test_une_adresse_active_est_evincee_apres_celles_qui_ne_le_sont_plus() -> None:
    limiteur, _ = un_limiteur(seuil_ecritures=2, cles_max=CLES_MAX_DU_TEST)
    for adresse in ("a", "b", "a", "c"):
        limiteur.consommer(adresse, ECRITURE)

    # « a » a été utilisée en dernier avant « c » : c'est « b » qui est oubliée.
    assert limiteur.consommer("a", ECRITURE) is not None
    assert limiteur.consommer("b", ECRITURE) is None
