"""Chargement des mappings SQL de tous les modules."""

from sqlalchemy import MetaData

from app.chantiers.infrastructure.sql.tables import TABLE_CHANTIERS
from app.etapes.infrastructure.sql.tables import TABLE_ETAPES, TABLE_HISTORIQUE_ETAPES

TABLES = (TABLE_CHANTIERS, TABLE_ETAPES, TABLE_HISTORIQUE_ETAPES)


def metadonnees() -> MetaData:
    """Renvoie les métadonnées de toutes les tables de l'application.

    Importer ce fichier charge le mapping de chaque module : c'est ce qu'attendent
    Alembic, qui compare ces métadonnées au schéma réel, et les tests de schéma.
    """
    return TABLES[0].metadata
