"""Migrations Alembic : application sur base vide, aller-retour, et cohérence avec les mappings."""

from pathlib import Path
from uuid import UUID

import pytest
from alembic import command
from alembic.script import ScriptDirectory
from sqlalchemy import Engine, inspect, text
from sqlalchemy.exc import IntegrityError

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


CHANTIER_AVEC_DOUBLON = UUID(int=1)
CHANTIER_SANS_DOUBLON = UUID(int=2)
INDEX_UNIQUE = "uq_etapes_chantier_id_ordre"
ETAPES_INSEREES = 5


def inserer_des_donnees_de_production(moteur: Engine) -> None:
    """Remplit une base au schéma 0001 : un chantier a deux étapes de même ordre.

    L'autre chantier a des ordres uniques, avec un trou (1 puis 4) que la migration
    doit laisser tel quel. Chaque étape a une entrée d'historique, que la migration ne
    doit surtout pas supprimer.
    """
    chantier = (
        "INSERT INTO chantiers VALUES (:id, 'Chantier', 'Rue', '69001', 'Lyon', "
        "'Client', '2026-01-01', '2026-06-01', 1000)"
    )
    etape = "INSERT INTO etapes VALUES (:id, :chantier, 'Étape', :ordre, 'en_cours', 2)"
    entree = (
        "INSERT INTO historique_etapes (etape_id, role, ancien_statut, nouveau_statut, date) "
        "VALUES (:id, 'chef', 'a_faire', 'en_cours', '2026-01-02 08:00:00')"
    )
    etapes = [
        (UUID(int=11), CHANTIER_AVEC_DOUBLON, 3),
        (UUID(int=12), CHANTIER_AVEC_DOUBLON, 3),
        (UUID(int=13), CHANTIER_AVEC_DOUBLON, 1),
        (UUID(int=21), CHANTIER_SANS_DOUBLON, 1),
        (UUID(int=22), CHANTIER_SANS_DOUBLON, 4),
    ]
    with moteur.begin() as connexion:
        for identifiant in (CHANTIER_AVEC_DOUBLON, CHANTIER_SANS_DOUBLON):
            connexion.execute(text(chantier), {"id": identifiant.hex})
        for identifiant, chantier_id, ordre in etapes:
            parametres = {"id": identifiant.hex, "chantier": chantier_id.hex, "ordre": ordre}
            connexion.execute(text(etape), parametres)
            connexion.execute(text(entree), {"id": identifiant.hex})


def lire_les_ordres(moteur: Engine) -> dict[int, int]:
    with moteur.connect() as connexion:
        lignes = connexion.execute(text("SELECT id, ordre FROM etapes"))
        return {UUID(hex=ligne.id).int: ligne.ordre for ligne in lignes}


def compter_l_historique(moteur: Engine) -> int:
    with moteur.connect() as connexion:
        return int(connexion.execute(text("SELECT count(*) FROM historique_etapes")).scalar_one())


def noms_d_index(moteur: Engine) -> set[str | None]:
    return {index["name"] for index in inspect(moteur).get_indexes("etapes")}


def test_la_migration_0002_renumerote_les_doublons_et_garde_toutes_les_donnees(
    tmp_path: Path,
) -> None:
    url = url_sqlite(tmp_path)
    configuration = configuration_alembic(url)
    command.upgrade(configuration, "0001")
    moteur = creer_moteur(url)
    inserer_des_donnees_de_production(moteur)

    command.upgrade(configuration, "0002")

    # Le doublon est départagé par l'identifiant ; l'autre chantier et son trou sont intacts.
    assert lire_les_ordres(moteur) == {11: 2, 12: 3, 13: 1, 21: 1, 22: 4}
    assert compter_l_historique(moteur) == ETAPES_INSEREES
    moteur.dispose()


def test_apres_la_migration_0002_un_ordre_deja_pris_est_refuse_par_la_base(tmp_path: Path) -> None:
    url = url_sqlite(tmp_path)
    configuration = configuration_alembic(url)
    command.upgrade(configuration, "0001")
    moteur = creer_moteur(url)
    inserer_des_donnees_de_production(moteur)
    command.upgrade(configuration, "0002")

    with pytest.raises(IntegrityError), moteur.begin() as connexion:
        connexion.execute(
            text("INSERT INTO etapes VALUES (:id, :chantier, 'Doublon', 4, 'a_faire', 1)"),
            {"id": UUID(int=99).hex, "chantier": CHANTIER_SANS_DOUBLON.hex},
        )

    assert INDEX_UNIQUE in noms_d_index(moteur)
    moteur.dispose()


def test_le_retour_a_0001_garde_les_donnees_et_retire_l_index_unique(tmp_path: Path) -> None:
    url = url_sqlite(tmp_path)
    configuration = configuration_alembic(url)
    command.upgrade(configuration, "0001")
    moteur = creer_moteur(url)
    inserer_des_donnees_de_production(moteur)
    command.upgrade(configuration, "0002")

    command.downgrade(configuration, "0001")

    assert noms_d_index(moteur) == {"ix_etapes_chantier_id"}
    assert compter_l_historique(moteur) == ETAPES_INSEREES
    assert len(lire_les_ordres(moteur)) == ETAPES_INSEREES
    moteur.dispose()
