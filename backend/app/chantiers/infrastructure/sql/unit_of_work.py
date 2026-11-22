"""Unit of Work SQL du module chantiers."""

from app.chantiers.infrastructure.sql.chantier_repository import SqlChantierRepository
from app.shared.infrastructure.sql.unit_of_work import SqlUnitOfWork


class SqlUnitOfWorkChantiers(SqlUnitOfWork):
    """Implémentation SQL de `UnitOfWorkChantiers` : donne accès au repository des chantiers."""

    @property
    def chantiers(self) -> SqlChantierRepository:
        """Le repository des chantiers, lié à la session de la transaction en cours."""
        return SqlChantierRepository(self.session)
