"""Crée les tables des chantiers, des étapes et de l'historique des étapes.

Revision ID: 0001
Revises:
Create Date: 2026-11-22
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0001"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _statut(nom: str) -> sa.Enum:
    """Colonne de statut d'étape : un texte limité aux quatre statuts du cycle."""
    return sa.Enum(
        "a_faire",
        "en_cours",
        "terminee_a_valider",
        "validee",
        name=nom,
        native_enum=False,
        create_constraint=True,
    )


def upgrade() -> None:
    """Crée les trois tables, avec leurs contraintes et leurs index."""
    op.create_table(
        "chantiers",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("nom", sa.String(), nullable=False),
        sa.Column("voie", sa.String(), nullable=False),
        sa.Column("code_postal", sa.String(length=10), nullable=False),
        sa.Column("ville", sa.String(), nullable=False),
        sa.Column("client", sa.String(), nullable=False),
        sa.Column("date_debut", sa.Date(), nullable=False),
        sa.Column("echeance", sa.Date(), nullable=False),
        sa.Column("budget_euros", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.CheckConstraint("budget_euros >= 0", name=op.f("ck_chantiers_budget_positif")),
        sa.CheckConstraint(
            "echeance >= date_debut", name=op.f("ck_chantiers_echeance_apres_debut")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_chantiers")),
    )
    op.create_table(
        "etapes",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("chantier_id", sa.Uuid(), nullable=False),
        sa.Column("titre", sa.String(), nullable=False),
        sa.Column("ordre", sa.Integer(), nullable=False),
        sa.Column("statut", _statut("statut"), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.CheckConstraint("ordre >= 1", name=op.f("ck_etapes_ordre_positif")),
        sa.CheckConstraint("version >= 1", name=op.f("ck_etapes_version_positive")),
        sa.ForeignKeyConstraint(
            ["chantier_id"], ["chantiers.id"], name=op.f("fk_etapes_chantier_id_chantiers")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_etapes")),
    )
    op.create_index(op.f("ix_etapes_chantier_id"), "etapes", ["chantier_id"], unique=False)
    op.create_table(
        "historique_etapes",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("etape_id", sa.Uuid(), nullable=False),
        sa.Column(
            "role",
            sa.Enum("chef", "ouvrier", name="role", native_enum=False, create_constraint=True),
            nullable=False,
        ),
        sa.Column("ancien_statut", _statut("ancien_statut"), nullable=False),
        sa.Column("nouveau_statut", _statut("nouveau_statut"), nullable=False),
        sa.Column("date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("commentaire", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(
            ["etape_id"],
            ["etapes.id"],
            name=op.f("fk_historique_etapes_etape_id_etapes"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_historique_etapes")),
    )
    op.create_index(
        op.f("ix_historique_etapes_etape_id"), "historique_etapes", ["etape_id"], unique=False
    )


def downgrade() -> None:
    """Supprime les trois tables, dans l'ordre inverse de leurs dépendances."""
    op.drop_index(op.f("ix_historique_etapes_etape_id"), table_name="historique_etapes")
    op.drop_table("historique_etapes")
    op.drop_index(op.f("ix_etapes_chantier_id"), table_name="etapes")
    op.drop_table("etapes")
    op.drop_table("chantiers")
