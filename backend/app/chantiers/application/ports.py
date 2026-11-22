"""Ports du module chantiers : ce dont ses cas d'usage ont besoin, et rien de plus."""

from collections.abc import Mapping, Sequence
from typing import Protocol
from uuid import UUID

from app.chantiers.domain.chantier import Chantier
from app.shared.application.ports import UnitOfWork


class ChantierRepository(Protocol):
    """Charge et enregistre des chantiers complets ; ne valide jamais la transaction."""

    def ajouter(self, chantier: Chantier) -> None:
        """Enregistre un nouveau chantier dans la transaction en cours."""
        ...

    def obtenir(self, chantier_id: UUID) -> Chantier:
        """Charge un chantier.

        Lève :
            NonTrouveError : aucun chantier n'a cet identifiant.
        """
        ...

    def lister(self) -> list[Chantier]:
        """Renvoie tous les chantiers, dans l'ordre de création (celui des UUID v7)."""
        ...


class UnitOfWorkChantiers(UnitOfWork, Protocol):
    """Transaction du module chantiers, qui donne accès à son repository."""

    @property
    def chantiers(self) -> ChantierRepository:
        """Le repository des chantiers, lié à la transaction en cours."""
        ...


class FournisseurAvancement(Protocol):
    """Donne l'avancement des chantiers, calculé par un autre module.

    chantiers ne connaît pas le module étapes : la composition root branche ce
    port sur le cas d'usage public `CalculerAvancements` d'étapes. La dépendance
    est ainsi inversée, et il n'y a pas d'import circulaire (intent.md, §2.3).
    """

    def executer(self, chantier_ids: Sequence[UUID]) -> Mapping[UUID, int]:
        """Renvoie, pour chaque identifiant demandé, un pourcentage entier de 0 à 100."""
        ...
