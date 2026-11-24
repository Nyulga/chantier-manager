"""Limite de débit tenue en mémoire : implémentation du port `LimiteurDebit`."""

import math
import threading
from collections import OrderedDict, deque
from collections.abc import Mapping
from datetime import datetime, timedelta

from app.shared.application.ports import CategorieAcces, Horloge

# Nombre maximal de couples (adresse, catégorie) suivis en même temps. Chacun garde au
# plus « seuil » horodatages (120 pour les lectures) : au pire 5 000 x 120 x ~60 octets,
# soit une quarantaine de Mo, bien sous la limite de 512 Mo du conteneur de l'API.
CLES_SUIVIES_MAX = 5_000


class MemoireLimiteurDebit:
    """Compte les accès de chaque adresse dans une fenêtre glissante, en mémoire.

    Pour chaque couple (adresse, catégorie), on garde les horodatages des accès permis
    dans la dernière fenêtre. Un accès est refusé quand ils atteignent le seuil, et le
    délai annoncé est celui où le plus ancien sort de la fenêtre : passé ce délai, le
    même accès est permis, ni plus tôt ni plus tard. Une fenêtre fixe aurait été plus
    courte à écrire, mais elle laisse passer le double du seuil à cheval sur deux
    fenêtres et annonce un délai moins précis.

    Hypothèse assumée (ADR 0016) : un seul processus API, donc un état en mémoire,
    perdu au redémarrage. Un verrou protège l'état, car FastAPI exécute les
    dépendances synchrones dans plusieurs fils d'exécution.

    Mémoire bornée de deux façons. Les clés expirées sont oubliées à chaque appel : le
    dictionnaire est classé par date du dernier accès permis, donc les plus anciennes
    sont en tête et l'oubli ne parcourt que ce qui expire. Si malgré tout il y a plus
    de `cles_max` clés (un flot d'adresses différentes), on oublie celle dont le
    dernier accès est le plus ancien, plutôt que de refuser les nouvelles adresses :
    refuser bloquerait les vrais visiteurs pendant l'attaque. Le prix est qu'une
    adresse évincée repart de zéro, ce qui n'avantage que celui qui contrôle déjà
    plus de `cles_max` adresses, et que ce plafond ne limite donc pas davantage.

    Chaque seuil doit valoir au moins 1, et `seuils` doit couvrir toutes les catégories.
    """

    def __init__(
        self,
        horloge: Horloge,
        seuils: Mapping[CategorieAcces, int],
        fenetre: timedelta,
        cles_max: int = CLES_SUIVIES_MAX,
    ) -> None:
        self._horloge = horloge
        self._seuils = seuils
        self._fenetre = fenetre
        self._cles_max = cles_max
        self._acces: OrderedDict[tuple[str, CategorieAcces], deque[datetime]] = OrderedDict()
        self._verrou = threading.Lock()

    def consommer(self, adresse: str, categorie: CategorieAcces) -> int | None:
        """Consomme une unité de `categorie` pour `adresse`, si le seuil le permet."""
        maintenant = self._horloge.maintenant()
        cle = (adresse, categorie)
        with self._verrou:
            self._oublier_les_cles_expirees(maintenant)
            horodatages = self._acces.get(cle, deque())
            self._oublier_les_acces_expires(horodatages, maintenant)
            if len(horodatages) >= self._seuils[categorie]:
                return self._delai_avant_reprise(horodatages[0], maintenant)
            horodatages.append(maintenant)
            self._retenir(cle, horodatages)
            return None

    def nombre_de_cles_suivies(self) -> int:
        """Renvoie le nombre de couples (adresse, catégorie) retenus, pour les tests."""
        with self._verrou:
            return len(self._acces)

    def _oublier_les_cles_expirees(self, maintenant: datetime) -> None:
        """Retire les clés dont le dernier accès est sorti de la fenêtre."""
        limite = maintenant - self._fenetre
        while self._acces and next(iter(self._acces.values()))[-1] <= limite:
            self._acces.popitem(last=False)

    def _oublier_les_acces_expires(
        self, horodatages: deque[datetime], maintenant: datetime
    ) -> None:
        """Retire les accès sortis de la fenêtre : à `fenetre` exactement, ils n'y sont plus."""
        limite = maintenant - self._fenetre
        while horodatages and horodatages[0] <= limite:
            horodatages.popleft()

    def _delai_avant_reprise(self, plus_ancien: datetime, maintenant: datetime) -> int:
        """Renvoie les secondes entières (arrondies au-dessus) avant que le plus ancien expire."""
        restant = plus_ancien + self._fenetre - maintenant
        return math.ceil(restant.total_seconds())

    def _retenir(self, cle: tuple[str, CategorieAcces], horodatages: deque[datetime]) -> None:
        """Place la clé en fin de classement, et évince la plus ancienne au-delà du plafond."""
        self._acces[cle] = horodatages
        self._acces.move_to_end(cle)
        if len(self._acces) > self._cles_max:
            self._acces.popitem(last=False)
