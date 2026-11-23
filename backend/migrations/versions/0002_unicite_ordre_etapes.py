"""Rend unique l'ordre des étapes d'un chantier.

Deux étapes d'un même chantier ne peuvent plus avoir le même ordre (issue #18).

C'est un index unique, et non une contrainte `UNIQUE` : sous SQLite, `ALTER TABLE`
ne sait pas ajouter une contrainte, et le mode « batch » d'Alembic recrée donc la
table (copie, suppression, renommage). Or la suppression de `etapes`, avec les clés
étrangères actives, supprime en cascade tout l'historique des transitions
(`ON DELETE CASCADE`) : la perte de données a été constatée. Un index se crée sans
toucher à la table, et protège exactement de la même façon. Pour la même raison,
les longueurs des colonnes texte, qui demanderaient de recréer `chantiers` et
`etapes`, sont reportées au passage à PostgreSQL (ADR 0007).

L'index unique commence par `chantier_id` : il remplace l'index simple qui existait
sur cette colonne, devenu redondant.

Les créations et suppressions d'index sont rejouables (`if_not_exists`, `if_exists`) : une
migration interrompue, ou un index créé à la main, ne bloque pas le démarrage de
l'application, qui applique les migrations à chaque lancement.

Les ordres sont normalement déjà uniques, puisque l'application les attribue à la
suite. Si une base contenait pourtant un doublon, la création de l'index échouerait :
les étapes d'un chantier concerné sont donc d'abord renumérotées de 1 à n, dans leur
ordre actuel, l'identifiant (croissant comme la date de création) départageant les
égalités. Seuls les chantiers qui ont un doublon sont touchés, et aucune donnée n'est
supprimée. Cette renumérotation n'est pas défaite par `downgrade`, qui ne retire que
l'index.

Revision ID: 0002
Revises: 0001
Create Date: 2026-11-23
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0002"
down_revision: str | Sequence[str] | None = "0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

ETAPES = sa.table(
    "etapes",
    sa.column("id", sa.Uuid()),
    sa.column("chantier_id", sa.Uuid()),
    sa.column("ordre", sa.Integer()),
)


def _renumeroter_les_chantiers_a_ordres_en_double() -> None:
    """Renumérote de 1 à n les étapes des chantiers qui ont deux étapes de même ordre."""
    connexion = op.get_bind()
    doublons = (
        sa.select(ETAPES.c.chantier_id)
        .group_by(ETAPES.c.chantier_id, ETAPES.c.ordre)
        .having(sa.func.count() > 1)
    )
    for chantier_id in set(connexion.execute(doublons).scalars()):
        etapes = connexion.execute(
            sa.select(ETAPES.c.id)
            .where(ETAPES.c.chantier_id == chantier_id)
            .order_by(ETAPES.c.ordre, ETAPES.c.id)
        ).scalars()
        for ordre, etape_id in enumerate(list(etapes), start=1):
            connexion.execute(sa.update(ETAPES).where(ETAPES.c.id == etape_id).values(ordre=ordre))


def upgrade() -> None:
    """Corrige les doublons éventuels, crée l'index unique, retire l'index simple."""
    _renumeroter_les_chantiers_a_ordres_en_double()
    op.create_index(
        op.f("uq_etapes_chantier_id_ordre"),
        "etapes",
        ["chantier_id", "ordre"],
        unique=True,
        if_not_exists=True,
    )
    op.drop_index(op.f("ix_etapes_chantier_id"), table_name="etapes", if_exists=True)


def downgrade() -> None:
    """Rétablit l'index simple sur le chantier et retire l'index unique."""
    op.create_index(
        op.f("ix_etapes_chantier_id"), "etapes", ["chantier_id"], unique=False, if_not_exists=True
    )
    op.drop_index(op.f("uq_etapes_chantier_id_ordre"), table_name="etapes", if_exists=True)
