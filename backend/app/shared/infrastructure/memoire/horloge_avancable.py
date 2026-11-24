"""Horloge de test dont on fait avancer l'instant à la main."""

from datetime import date, datetime, timedelta

from app.shared.infrastructure.fuseau_metier import date_metier


class HorlogeAvancable:
    """Implémentation du port `Horloge` qui ne bouge que lorsqu'on l'avance.

    Les règles qui dépendent du temps qui passe (limite de débit, durée d'un
    blocage) se testent sans `sleep` : le test avance l'horloge du délai voulu, de
    façon exacte et déterministe. `HorlogeFixe` suffit quand le temps ne compte pas.
    """

    def __init__(self, instant: datetime) -> None:
        self._instant = instant

    def maintenant(self) -> datetime:
        """Renvoie l'instant courant, tel que les appels à `avancer` l'ont fait évoluer."""
        return self._instant

    def aujourd_hui(self) -> date:
        """Renvoie la date à Paris de l'instant courant, comme l'horloge système."""
        return date_metier(self._instant)

    def avancer(self, duree: timedelta) -> None:
        """Fait avancer l'horloge de `duree`."""
        self._instant += duree
