"""Horloge de test qui renvoie toujours le même instant."""

from datetime import date, datetime

from app.shared.infrastructure.fuseau_metier import date_metier


class HorlogeFixe:
    """Implémentation du port `Horloge` figée sur un instant donné, pour des tests déterministes.

    Sa date du jour suit la même règle que l'horloge système (la date à Paris), pour
    que les tests des cas d'usage voient les mêmes dates qu'en production.
    """

    def __init__(self, instant: datetime) -> None:
        self._instant = instant

    def maintenant(self) -> datetime:
        """Renvoie l'instant fixé à la construction, à chaque appel."""
        return self._instant

    def aujourd_hui(self) -> date:
        """Renvoie la date à Paris de l'instant fixé."""
        return date_metier(self._instant)
