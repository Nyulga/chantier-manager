"""Reconnaissance des erreurs de base qui sont de vraies indisponibilités."""

import sqlite3

from sqlalchemy.exc import OperationalError

# SQLite compose ses codes étendus (`SQLITE_IOERR_READ`…) à partir d'un code primaire,
# qu'on retrouve dans l'octet de poids faible.
MASQUE_CODE_PRIMAIRE = 0xFF

# Les codes primaires de SQLite qui désignent une base momentanément hors d'atteinte :
# occupée ou verrouillée par une autre connexion, fichier impossible à ouvrir, erreur
# d'entrée-sortie, disque plein. Un autre code (`SQLITE_ERROR` : table absente, syntaxe
# fautive…) est un défaut du programme. Ajouter un cas, c'est ajouter une ligne ici.
CODES_INDISPONIBILITE_SQLITE = frozenset(
    {
        sqlite3.SQLITE_BUSY,
        sqlite3.SQLITE_LOCKED,
        # Un volume pas encore monté ou des droits passagers relèvent d'une indisponibilité.
        # Un chemin mal configuré reste diagnostiquable : la cause complète est journalisée.
        sqlite3.SQLITE_CANTOPEN,
        sqlite3.SQLITE_IOERR,
        sqlite3.SQLITE_FULL,
    }
)


def est_indisponibilite(erreur: OperationalError) -> bool:
    """Dit si l'erreur opérationnelle vient d'une base injoignable, et non d'un bogue.

    Toutes les erreurs opérationnelles ne méritent pas un « réessaie dans un instant » :
    réessayer une requête sur une table absente échouera toujours, et cacher cette
    cause derrière un 503 empêcherait de la voir. On lit le code d'erreur du pilote
    (`sqlite_errorcode`) plutôt que son message, qui change d'une version à l'autre ;
    SQLAlchemy signale lui-même une connexion perdue (`connection_invalidated`).
    """
    if erreur.connection_invalidated:
        return True
    code = getattr(erreur.orig, "sqlite_errorcode", None)
    return code is not None and code & MASQUE_CODE_PRIMAIRE in CODES_INDISPONIBILITE_SQLITE
