"""Reconnaissance d'une violation d'unicité parmi les erreurs d'intégrité de la base."""

import sqlite3

import pytest
from sqlalchemy.exc import IntegrityError

from app.shared.infrastructure.sql.violation_unicite import est_violation_unicite

SQLSTATE_UNICITE = "23505"
SQLSTATE_CLE_ETRANGERE = "23503"


class ErreurPostgresError(Exception):
    """Erreur d'un pilote PostgreSQL : seul son code SQLSTATE nous intéresse."""

    def __init__(self, sqlstate: str) -> None:
        super().__init__("erreur simulée")
        self.sqlstate = sqlstate


def erreur_sqlite(instructions: list[str]) -> IntegrityError:
    """Provoque une vraie erreur d'intégrité SQLite avec la dernière instruction."""
    connexion = sqlite3.connect(":memory:")
    connexion.execute("PRAGMA foreign_keys=ON")
    *preparation, fautive = instructions
    for instruction in preparation:
        connexion.execute(instruction)
    try:
        connexion.execute(fautive)
    except sqlite3.IntegrityError as origine:
        return IntegrityError(fautive, {}, origine)
    finally:
        connexion.close()
    raise AssertionError("L'instruction aurait dû violer une contrainte.")


def test_une_valeur_deja_prise_dans_un_index_unique_sqlite_est_une_violation_d_unicite() -> None:
    erreur = erreur_sqlite(
        [
            "CREATE TABLE t (a INTEGER, b INTEGER)",
            "CREATE UNIQUE INDEX uq_t ON t (a, b)",
            "INSERT INTO t VALUES (1, 1)",
            "INSERT INTO t VALUES (1, 1)",
        ]
    )

    assert est_violation_unicite(erreur) is True


def test_une_cle_primaire_en_double_sqlite_est_une_violation_d_unicite() -> None:
    erreur = erreur_sqlite(
        [
            "CREATE TABLE t (a INTEGER PRIMARY KEY)",
            "INSERT INTO t VALUES (1)",
            "INSERT INTO t VALUES (1)",
        ]
    )

    assert est_violation_unicite(erreur) is True


def test_une_cle_etrangere_sqlite_violee_n_est_pas_une_violation_d_unicite() -> None:
    erreur = erreur_sqlite(
        [
            "CREATE TABLE parent (id INTEGER PRIMARY KEY)",
            "CREATE TABLE enfant (parent_id INTEGER REFERENCES parent (id))",
            "INSERT INTO enfant VALUES (7)",
        ]
    )

    assert est_violation_unicite(erreur) is False


@pytest.mark.parametrize(
    ("sqlstate", "attendu"), [(SQLSTATE_UNICITE, True), (SQLSTATE_CLE_ETRANGERE, False)]
)
def test_postgresql_signale_l_unicite_par_son_code_sqlstate(sqlstate: str, attendu: bool) -> None:
    erreur = IntegrityError("INSERT", {}, ErreurPostgresError(sqlstate))

    assert est_violation_unicite(erreur) is attendu


def test_une_erreur_dont_l_origine_n_a_aucun_code_connu_n_est_pas_une_violation_d_unicite() -> None:
    erreur = IntegrityError("INSERT", {}, Exception("origine inconnue"))

    assert est_violation_unicite(erreur) is False
