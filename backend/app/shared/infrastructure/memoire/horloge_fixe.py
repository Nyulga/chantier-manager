"""Horloge de test qui renvoie toujours le même instant."""

from datetime import datetime


class HorlogeFixe:
    """Implémentation du port `Horloge` figée sur un instant donné, pour des tests déterministes."""

    def __init__(self, instant: datetime) -> None:
        self._instant = instant

    def maintenant(self) -> datetime:
        """Renvoie l'instant fixé à la construction, à chaque appel."""
        return self._instant
