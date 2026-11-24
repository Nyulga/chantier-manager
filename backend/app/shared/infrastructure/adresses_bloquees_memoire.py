"""Liste d'adresses bloquées tenue en mémoire : implémentation du port `ListeAdressesBloquees`."""

import threading
from collections import OrderedDict
from datetime import datetime, timedelta

from app.shared.application.ports import Horloge

# Nombre maximal d'adresses bloquées en même temps : une entrée pèse quelques centaines
# d'octets, soit quelques Mo au plus.
ADRESSES_BLOQUEES_MAX = 10_000


class MemoireListeAdressesBloquees:
    """Retient en mémoire la fin du blocage de chaque adresse.

    Hypothèse assumée (ADR 0015) : un seul processus API, donc une liste perdue au
    redémarrage. Un verrou protège l'état, car FastAPI exécute les dépendances
    synchrones dans plusieurs fils d'exécution.

    Tous les blocages ont la même durée : le dictionnaire, classé par fin de blocage,
    a donc les plus proches de l'expiration en tête. L'oubli des blocages expirés ne
    parcourt que ce qui expire, et rebloquer une adresse la replace en fin de
    classement, ce qui fait repartir sa durée de zéro.

    Si le plafond `adresses_max` est dépassé (un flot d'adresses différentes qui
    touchent le piège), on oublie le blocage le plus proche de son terme : c'est celui
    dont la perte coûte le moins de protection, et refuser de bloquer une nouvelle
    adresse laisserait un robot continuer ses écritures.
    """

    def __init__(
        self,
        horloge: Horloge,
        duree: timedelta,
        adresses_max: int = ADRESSES_BLOQUEES_MAX,
    ) -> None:
        self._horloge = horloge
        self._duree = duree
        self._adresses_max = adresses_max
        self._fins: OrderedDict[str, datetime] = OrderedDict()
        self._verrou = threading.Lock()

    def bloquer(self, adresse: str) -> None:
        """Bloque `adresse` pour toute la durée, à partir de maintenant."""
        maintenant = self._horloge.maintenant()
        with self._verrou:
            self._oublier_les_blocages_expires(maintenant)
            self._fins[adresse] = maintenant + self._duree
            self._fins.move_to_end(adresse)
            if len(self._fins) > self._adresses_max:
                self._fins.popitem(last=False)

    def est_bloquee(self, adresse: str) -> bool:
        """Indique si `adresse` est bloquée en ce moment (la durée n'est pas écoulée)."""
        with self._verrou:
            self._oublier_les_blocages_expires(self._horloge.maintenant())
            return adresse in self._fins

    def nombre_d_adresses_bloquees(self) -> int:
        """Renvoie le nombre d'adresses retenues, pour les tests."""
        with self._verrou:
            return len(self._fins)

    def _oublier_les_blocages_expires(self, maintenant: datetime) -> None:
        """Retire les blocages dont la fin est atteinte : à la durée exacte, l'adresse est libre."""
        while self._fins and next(iter(self._fins.values())) <= maintenant:
            self._fins.popitem(last=False)
