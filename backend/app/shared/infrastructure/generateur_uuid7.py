"""Générateur d'identifiants UUID v7 (RFC 9562), sans dépendance externe."""

import secrets
import time
from collections.abc import Callable
from threading import Lock
from uuid import UUID

DECALAGE_HORODATAGE = 80  # Les 48 premiers bits portent la date en millisecondes.
VERSION_7 = 0x7
DECALAGE_VERSION = 76
DECALAGE_COMPTEUR = 64  # Les 12 bits suivants portent le compteur de la milliseconde.
COMPTEUR_MAX = 0xFFF
VARIANTE_RFC = 0b10
DECALAGE_VARIANTE = 62
BITS_ALEATOIRES = 62
NANOSECONDES_PAR_MILLISECONDE = 1_000_000


def _millisecondes_systeme() -> int:
    return time.time_ns() // NANOSECONDES_PAR_MILLISECONDE


class GenerateurUuid7:
    """Implémentation du port `GenerateurId` qui produit des UUID v7 (intent.md, §2.3).

    Python 3.13 n'a pas encore `uuid.uuid7` : la structure de la RFC 9562 est donc
    construite ici. Les identifiants sont strictement croissants dans le processus,
    même au sein d'une milliseconde (un compteur de 12 bits occupe la place prévue
    par la RFC) : les repositories s'appuient sur cet ordre pour lister « dans
    l'ordre de création ». Si l'horloge recule, le dernier horodatage est conservé,
    pour que l'ordre ne s'inverse jamais.
    """

    def __init__(self, horloge_ms: Callable[[], int] = _millisecondes_systeme) -> None:
        self._horloge_ms = horloge_ms
        self._dernier_ms = 0
        self._compteur = 0
        # Les routes synchrones de FastAPI s'exécutent dans plusieurs threads.
        self._verrou = Lock()

    def nouveau(self) -> UUID:
        """Renvoie un nouvel identifiant, supérieur à tous ceux déjà distribués."""
        with self._verrou:
            horodatage, compteur = self._prochain_couple()
        aleatoire = secrets.randbits(BITS_ALEATOIRES)
        return UUID(
            int=(horodatage << DECALAGE_HORODATAGE)
            | (VERSION_7 << DECALAGE_VERSION)
            | (compteur << DECALAGE_COMPTEUR)
            | (VARIANTE_RFC << DECALAGE_VARIANTE)
            | aleatoire
        )

    def _prochain_couple(self) -> tuple[int, int]:
        """Choisit l'horodatage et le compteur ; l'appelant détient le verrou."""
        horodatage = max(self._horloge_ms(), self._dernier_ms)
        if horodatage == self._dernier_ms:
            self._compteur += 1
            if self._compteur > COMPTEUR_MAX:
                # Plus de 4096 identifiants dans la même milliseconde : on avance
                # d'une milliseconde plutôt que de rompre l'ordre.
                horodatage += 1
                self._compteur = 0
        else:
            self._compteur = 0
        self._dernier_ms = horodatage
        return horodatage, self._compteur
