"""Distinction entre une vraie indisponibilité de la base et un défaut du programme."""

import sqlite3
from pathlib import Path

import pytest
from app.shared.infrastructure.sql.indisponibilite import est_indisponibilite
from sqlalchemy.exc import OperationalError


class ErreurSqliteError(Exception):
    """Erreur d'un pilote SQLite : seul son code d'erreur nous intéresse."""

    def __init__(self, code: int) -> None:
        super().__init__("erreur simulée")
        self.sqlite_errorcode = code


def erreur_operationnelle(code: int) -> OperationalError:
    return OperationalError("SELECT", {}, ErreurSqliteError(code))


@pytest.mark.parametrize(
    "code",
    [
        sqlite3.SQLITE_BUSY,
        sqlite3.SQLITE_LOCKED,
        sqlite3.SQLITE_CANTOPEN,
        sqlite3.SQLITE_IOERR,
        sqlite3.SQLITE_FULL,
        sqlite3.SQLITE_IOERR_READ,
        sqlite3.SQLITE_BUSY_SNAPSHOT,
    ],
    ids=[
        "occupee",
        "verrouillee",
        "impossible-a-ouvrir",
        "entree-sortie",
        "disque-plein",
        "entree-sortie-etendu",
        "occupee-etendu",
    ],
)
def test_une_base_occupee_verrouillee_ou_illisible_est_une_indisponibilite(code: int) -> None:
    assert est_indisponibilite(erreur_operationnelle(code)) is True


def test_une_connexion_perdue_est_une_indisponibilite() -> None:
    erreur = OperationalError(
        "SELECT", {}, Exception("connexion coupée"), connection_invalidated=True
    )

    assert est_indisponibilite(erreur) is True


def test_une_table_absente_est_un_defaut_du_programme() -> None:
    connexion = sqlite3.connect(":memory:")
    with pytest.raises(sqlite3.OperationalError) as origine:
        connexion.execute("SELECT * FROM absente")
    connexion.close()

    assert est_indisponibilite(OperationalError("SELECT", {}, origine.value)) is False


def test_une_erreur_de_syntaxe_est_un_defaut_du_programme() -> None:
    assert est_indisponibilite(erreur_operationnelle(sqlite3.SQLITE_ERROR)) is False


def test_une_erreur_sans_code_connu_n_est_pas_une_indisponibilite() -> None:
    assert est_indisponibilite(OperationalError("SELECT", {}, Exception("inconnue"))) is False


def test_une_vraie_base_verrouillee_par_un_autre_est_une_indisponibilite(tmp_path: Path) -> None:
    fichier = tmp_path / "verrou.db"
    verrou = sqlite3.connect(fichier, isolation_level=None)
    verrou.execute("CREATE TABLE t (a INTEGER)")
    verrou.execute("BEGIN EXCLUSIVE")
    lecteur = sqlite3.connect(fichier, timeout=0)

    with pytest.raises(sqlite3.OperationalError) as origine:
        lecteur.execute("SELECT * FROM t")
    lecteur.close()
    verrou.close()

    assert est_indisponibilite(OperationalError("SELECT", {}, origine.value)) is True
