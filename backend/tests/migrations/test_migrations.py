"""Migrations Alembic : application sur base vide, aller-retour, et cohérence avec les mappings."""

from pathlib import Path

from alembic import command
from alembic.script import ScriptDirectory
from sqlalchemy import inspect

from app.composition.base_de_donnees import configuration_alembic
from app.shared.infrastructure.sql.moteur import creer_moteur
from tests.conftest import url_sqlite

TABLES = {"chantiers", "etapes", "historique_etapes"}


def tables_presentes(url: str) -> set[str]:
    moteur = creer_moteur(url)
    try:
        return set(inspect(moteur).get_table_names()) - {"alembic_version"}
    finally:
        moteur.dispose()


def test_la_migration_initiale_cree_les_tables_sur_une_base_vide(tmp_path: Path) -> None:
    url = url_sqlite(tmp_path)

    command.upgrade(configuration_alembic(url), "head")

    assert tables_presentes(url) == TABLES


def test_les_migrations_sont_reversibles_et_rejouables(tmp_path: Path) -> None:
    url = url_sqlite(tmp_path)
    configuration = configuration_alembic(url)

    command.upgrade(configuration, "head")
    command.downgrade(configuration, "base")
    vide = tables_presentes(url)
    command.upgrade(configuration, "head")

    assert vide == set()
    assert tables_presentes(url) == TABLES


def test_le_schema_des_migrations_correspond_aux_mappings(tmp_path: Path) -> None:
    configuration = configuration_alembic(url_sqlite(tmp_path))
    command.upgrade(configuration, "head")

    # `check` lève une erreur s'il détecte la moindre différence avec les mappings.
    command.check(configuration)


def test_il_n_y_a_qu_une_seule_tete_de_migration(tmp_path: Path) -> None:
    script = ScriptDirectory.from_config(configuration_alembic(url_sqlite(tmp_path)))

    assert len(script.get_heads()) == 1
