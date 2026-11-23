"""Environnement d'exécution d'Alembic : relie les migrations à la base et aux mappings."""

from alembic import context
from sqlalchemy import Connection

from app.composition.mapping import metadonnees
from app.composition.parametres import Parametres
from app.shared.infrastructure.sql.moteur import creer_moteur

config = context.config
cible = metadonnees()


def executer_migrations(connexion: Connection) -> None:
    """Applique les migrations sur une connexion ouverte."""
    # `render_as_batch` : SQLite ne sait pas modifier une colonne sur place, ni ajouter
    # une contrainte. Le mode batch recrée alors la table, et la suppression de l'ancienne
    # supprime en cascade les lignes des tables qui la référencent avec `ON DELETE CASCADE`
    # (l'historique des étapes) : avant d'écrire une migration batch sur une table
    # référencée, il faut désactiver les clés étrangères, ou préférer un index (0002).
    context.configure(connection=connexion, target_metadata=cible, render_as_batch=True)
    with context.begin_transaction():
        context.run_migrations()


def migrer_en_ligne() -> None:
    """Se connecte à la base puis migre.

    L'URL vient du code appelant (démarrage de l'application, tests) ; à défaut, de
    la configuration de l'application, ce qui sert à la ligne de commande `alembic`.
    """
    url_base = config.attributes.get("url_base") or Parametres().url_base
    moteur = creer_moteur(url_base)
    with moteur.connect() as connexion:
        executer_migrations(connexion)
    moteur.dispose()


migrer_en_ligne()
