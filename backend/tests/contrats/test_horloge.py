"""Contrat du port `Horloge` : joué sur l'horloge système et sur l'horloge fixe des tests."""

from datetime import timedelta

from app.shared.application.ports import Horloge
from app.shared.infrastructure.fuseau_metier import date_metier


def test_l_instant_present_est_en_utc(horloge: Horloge) -> None:
    assert horloge.maintenant().utcoffset() == timedelta(0)


def test_l_instant_present_ne_recule_pas(horloge: Horloge) -> None:
    premier = horloge.maintenant()

    second = horloge.maintenant()

    assert premier <= second


def test_la_date_du_jour_est_celle_de_paris_a_l_instant_present(horloge: Horloge) -> None:
    # Encadrer l'appel par deux lectures rend le test sûr même s'il passe minuit.
    avant = date_metier(horloge.maintenant())

    aujourd_hui = horloge.aujourd_hui()

    assert avant <= aujourd_hui <= date_metier(horloge.maintenant())
