"""Unit of Work mémoire du module étapes, pour les tests."""

from app.etapes.infrastructure.memoire.etape_repository import MemoireEtapeRepository
from app.shared.infrastructure.memoire.unit_of_work import MemoireUnitOfWork


class MemoireUnitOfWorkEtapes(MemoireUnitOfWork):
    """Implémentation mémoire de `UnitOfWorkEtapes` : sa transaction couvre les étapes."""

    def __init__(self) -> None:
        self.etapes = MemoireEtapeRepository()
        super().__init__(self.etapes)
