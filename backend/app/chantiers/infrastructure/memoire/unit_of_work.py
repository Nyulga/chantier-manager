"""Unit of Work mémoire du module chantiers, pour les tests."""

from app.chantiers.infrastructure.memoire.chantier_repository import MemoireChantierRepository
from app.shared.infrastructure.memoire.unit_of_work import MemoireUnitOfWork


class MemoireUnitOfWorkChantiers(MemoireUnitOfWork):
    """Implémentation mémoire de `UnitOfWorkChantiers` : sa transaction couvre les chantiers."""

    def __init__(self) -> None:
        self.chantiers = MemoireChantierRepository()
        super().__init__(self.chantiers)
