"""Fuseau horaire de la date métier : celui de l'entreprise, en France métropolitaine.

Les instants sont enregistrés en UTC, mais une date « du jour » (pour savoir si un
chantier est en retard, par exemple) est celle que vivent les utilisateurs sur le
terrain. Sans cette conversion, entre minuit et 1 h (2 h en été) à Paris, la date UTC
serait encore celle de la veille, et un chantier dont l'échéance vient de passer
apparaîtrait « à échéance aujourd'hui » au lieu d'« en retard ».

Les deux horloges (système et fixe) passent par cette même fonction : le test de
l'horloge fixe prouve ainsi la règle appliquée en production.
"""

from datetime import date, datetime
from zoneinfo import ZoneInfo

# Le fuseau de Paris tient compte de l'heure d'été. Ses données viennent du système ou,
# à défaut (Windows, images minimales), du paquet `tzdata` installé avec l'application.
FUSEAU_METIER = ZoneInfo("Europe/Paris")


def date_metier(instant: datetime) -> date:
    """Renvoie la date, à Paris, d'un instant qui porte son fuseau horaire."""
    return instant.astimezone(FUSEAU_METIER).date()
