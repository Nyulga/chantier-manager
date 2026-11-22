"""Tables des étapes et de leur historique, avec leur mapping impératif (Data Mapper).

Les entités `Etape` et `HistoriqueEtape` restent des dataclasses pures : le mapping
les instrumente à l'import de ce fichier, sans classe ORM en double (ADR 0002).
"""

from sqlalchemy import CheckConstraint, Column, ForeignKey, Integer, String, Table, Uuid
from sqlalchemy.orm import relationship

from app.etapes.domain.cycle import StatutEtape
from app.etapes.domain.etape import Etape, HistoriqueEtape
from app.shared.domain.acteur import Role
from app.shared.infrastructure.sql.registre import metadata, registre
from app.shared.infrastructure.sql.types import DateHeureUtc, enum_texte

# Les clés étrangères désignent la table par son nom : étapes n'importe rien de
# l'infrastructure de chantiers (contrat import-linter), mais la base vérifie le lien.
TABLE_ETAPES = Table(
    "etapes",
    metadata,
    Column("id", Uuid, primary_key=True),
    Column("chantier_id", Uuid, ForeignKey("chantiers.id"), nullable=False, index=True),
    Column("titre", String, nullable=False),
    Column("ordre", Integer, nullable=False),
    Column("statut", enum_texte(StatutEtape, "statut"), nullable=False),
    Column("version", Integer, nullable=False),
    CheckConstraint("ordre >= 1", name="ordre_positif"),
    CheckConstraint("version >= 1", name="version_positive"),
)

# Une entrée d'historique n'a pas d'identifiant dans le domaine : l'identifiant de
# cette table est une clé technique, qui sert aussi à départager deux entrées de
# même date.
TABLE_HISTORIQUE_ETAPES = Table(
    "historique_etapes",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column(
        "etape_id", Uuid, ForeignKey("etapes.id", ondelete="CASCADE"), nullable=False, index=True
    ),
    Column("role", enum_texte(Role, "role"), nullable=False),
    Column("ancien_statut", enum_texte(StatutEtape, "ancien_statut"), nullable=False),
    Column("nouveau_statut", enum_texte(StatutEtape, "nouveau_statut"), nullable=False),
    Column("date", DateHeureUtc, nullable=False),
    Column("commentaire", String, nullable=True),
)

registre.map_imperatively(HistoriqueEtape, TABLE_HISTORIQUE_ETAPES)

registre.map_imperatively(
    Etape,
    TABLE_ETAPES,
    # Le verrou optimiste (intent.md, §2.3) : l'UPDATE ne réussit que si la version
    # en base est celle qui a été lue. Le domaine incrémente lui-même `version`
    # (`generator=False`), pour que la règle reste dans le domaine.
    version_id_col=TABLE_ETAPES.c.version,
    version_id_generator=False,
    properties={
        # Chargé avec l'étape (« selectin ») : pas une requête par étape listée.
        "historique": relationship(
            HistoriqueEtape,
            order_by=[TABLE_HISTORIQUE_ETAPES.c.date, TABLE_HISTORIQUE_ETAPES.c.id],
            cascade="all, delete-orphan",
            lazy="selectin",
        )
    },
)
