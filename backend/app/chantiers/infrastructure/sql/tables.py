"""Table des chantiers et son mapping impératif (Data Mapper, règle 03).

L'entité `Chantier` reste une dataclass pure : le mapping l'instrumente à
l'import de ce fichier, sans classe ORM en double (ADR 0002).
"""

from sqlalchemy import CheckConstraint, Column, Date, Numeric, String, Table, Uuid
from sqlalchemy.orm import composite

from app.chantiers.domain.adresse import Adresse
from app.chantiers.domain.chantier import Chantier
from app.chantiers.domain.montant import Montant
from app.shared.infrastructure.sql.registre import metadata, registre

CODE_POSTAL_LONGUEUR_MAX = 10

TABLE_CHANTIERS = Table(
    "chantiers",
    metadata,
    Column("id", Uuid, primary_key=True),
    Column("nom", String, nullable=False),
    Column("voie", String, nullable=False),
    Column("code_postal", String(CODE_POSTAL_LONGUEUR_MAX), nullable=False),
    Column("ville", String, nullable=False),
    Column("client", String, nullable=False),
    Column("date_debut", Date, nullable=False),
    Column("echeance", Date, nullable=False),
    # La colonne ne s'appelle pas `budget` : ce nom est celui de l'attribut composite
    # du domaine, et les deux entreraient en conflit dans le mapping.
    Column("budget_euros", Numeric(12, 2), nullable=False),
    # Défense en profondeur : le domaine garantit déjà ces règles (règle 07).
    CheckConstraint("budget_euros >= 0", name="budget_positif"),
    CheckConstraint("echeance >= date_debut", name="echeance_apres_debut"),
)

registre.map_imperatively(
    Chantier,
    TABLE_CHANTIERS,
    properties={
        "adresse": composite(
            Adresse,
            TABLE_CHANTIERS.c.voie,
            TABLE_CHANTIERS.c.code_postal,
            TABLE_CHANTIERS.c.ville,
        ),
        "budget": composite(Montant, TABLE_CHANTIERS.c.budget_euros),
    },
)
