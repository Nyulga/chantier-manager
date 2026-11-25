"""Seuils de la limite de débit : ce sont des décisions du propriétaire (lot S6).

Le test les fige : un changement de seuil doit être voulu, et donc visible dans la
revue, puisqu'il oblige à modifier ce test en même temps que la constante.
"""

from datetime import timedelta

from app.shared.application.limites_debit import (
    DUREE_BLOCAGE_PIEGE,
    ECRITURES_PAR_FENETRE,
    FACTEUR_BLOC_IPV6_48,
    FENETRE_DEBIT,
    LECTURES_PAR_FENETRE,
)


def test_une_adresse_a_droit_a_20_ecritures_et_120_lectures_par_minute() -> None:
    seuils = (FENETRE_DEBIT, ECRITURES_PAR_FENETRE, LECTURES_PAR_FENETRE)

    assert seuils == (timedelta(seconds=60), 20, 120)


def test_une_adresse_qui_touche_un_piege_est_bloquee_une_heure() -> None:
    blocage = DUREE_BLOCAGE_PIEGE

    assert blocage == timedelta(hours=1)


def test_un_bloc_ipv6_48_a_droit_a_quatre_fois_les_seuils_d_une_adresse() -> None:
    seuils_du_bloc = (
        ECRITURES_PAR_FENETRE * FACTEUR_BLOC_IPV6_48,
        LECTURES_PAR_FENETRE * FACTEUR_BLOC_IPV6_48,
    )

    assert (FACTEUR_BLOC_IPV6_48, seuils_du_bloc) == (4, (80, 480))
