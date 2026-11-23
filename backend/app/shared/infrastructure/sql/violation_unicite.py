"""Reconnaissance d'une violation d'unicité parmi les erreurs d'intégrité de la base."""

import sqlite3

from sqlalchemy.exc import IntegrityError

# Code SQLSTATE standard d'une contrainte d'unicité violée, renvoyé par PostgreSQL.
SQLSTATE_UNICITE = "23505"
CODES_UNICITE_SQLITE = frozenset(
    {sqlite3.SQLITE_CONSTRAINT_UNIQUE, sqlite3.SQLITE_CONSTRAINT_PRIMARYKEY}
)


def est_violation_unicite(erreur: IntegrityError) -> bool:
    """Dit si l'erreur d'intégrité vient d'une valeur déjà prise dans un index unique.

    Les autres contraintes (clé étrangère, `CHECK`, `NOT NULL`) signalent un défaut
    du programme, et non un conflit entre deux utilisateurs : elles ne doivent pas
    être confondues avec lui. On lit le code d'erreur du pilote, plutôt que son
    message, qui change d'une version à l'autre. SQLite le donne dans
    `sqlite_errorcode`, PostgreSQL (psycopg) dans `sqlstate`.
    """
    origine = erreur.orig
    return (
        getattr(origine, "sqlite_errorcode", None) in CODES_UNICITE_SQLITE
        or getattr(origine, "sqlstate", None) == SQLSTATE_UNICITE
    )
