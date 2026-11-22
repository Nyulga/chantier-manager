"""Unit of Work SQL du module étapes."""

from app.etapes.infrastructure.sql.etape_repository import SqlEtapeRepository
from app.shared.infrastructure.sql.unit_of_work import SqlUnitOfWork


class SqlUnitOfWorkEtapes(SqlUnitOfWork):
    """Implémentation SQL de `UnitOfWorkEtapes` : donne accès au repository des étapes."""

    @property
    def etapes(self) -> SqlEtapeRepository:
        """Le repository des étapes, lié à la session de la transaction en cours."""
        return SqlEtapeRepository(self.session)
