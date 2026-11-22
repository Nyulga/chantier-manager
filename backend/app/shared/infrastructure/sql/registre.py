"""Registre de mapping impératif, partagé par tous les modules (ADR 0002).

Un seul registre et une seule `MetaData` : Alembic compare ainsi toutes les tables
d'un coup, et les clés étrangères entre modules se déclarent par le nom de la
table, sans importer l'infrastructure d'un autre module.
"""

from sqlalchemy import MetaData
from sqlalchemy.orm import registry

# Des noms de contraintes déterministes : sans eux, la base en génère elle-même,
# et Alembic ne saurait pas les supprimer proprement dans une migration future.
CONVENTION_DE_NOMS = {
    "ix": "ix_%(table_name)s_%(column_0_name)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

metadata = MetaData(naming_convention=CONVENTION_DE_NOMS)
registre = registry(metadata=metadata)
