"""Horloge réelle : l'heure du système, en UTC, et la date du jour à Paris."""

from datetime import UTC, date, datetime

from app.shared.infrastructure.fuseau_metier import date_metier


class HorlogeSysteme:
    """Implémentation du port `Horloge` qui lit l'heure du système.

    L'heure est toujours en UTC et porte son fuseau : les instants enregistrés en
    base ne dépendent ainsi ni du réglage du serveur ni de l'heure d'été. La date du
    jour, elle, est celle de Paris (voir `fuseau_metier`).
    """

    def maintenant(self) -> datetime:
        """Renvoie l'instant présent, en UTC."""
        return datetime.now(UTC)

    def aujourd_hui(self) -> date:
        """Renvoie la date du jour à Paris, quel que soit le fuseau du serveur."""
        return date_metier(self.maintenant())
