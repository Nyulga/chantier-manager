"""Horloge réelle : l'heure du système, en UTC."""

from datetime import UTC, datetime


class HorlogeSysteme:
    """Implémentation du port `Horloge` qui lit l'heure du système.

    L'heure est toujours en UTC et porte son fuseau : les instants enregistrés en
    base ne dépendent ainsi ni du réglage du serveur ni de l'heure d'été.
    """

    def maintenant(self) -> datetime:
        """Renvoie l'instant présent, en UTC."""
        return datetime.now(UTC)
