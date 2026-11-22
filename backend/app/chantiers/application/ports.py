"""Ports du module chantiers : ce dont ses cas d'usage ont besoin, et rien de plus."""

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Final, Protocol
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


@dataclass(frozen=True)
class ResumeEtapes:
    """Résumé des étapes d'un chantier, tel que le module étapes le calcule.

    `avancement` est un pourcentage entier de 0 à 100. `validees` compte les étapes
    validées, `a_valider` celles qui attendent la décision d'un chef, et `total`
    toutes les étapes du chantier. chantiers ne fait que les afficher : le calcul,
    et donc la règle, appartiennent au domaine d'étapes.
    """

    avancement: int
    validees: int
    total: int
    a_valider: int


# Résumé d'un chantier qui n'a encore aucune étape : 0 % et aucun compteur.
RESUME_SANS_ETAPE: Final = ResumeEtapes(avancement=0, validees=0, total=0, a_valider=0)


class FournisseurResumeEtapes(Protocol):
    """Donne le résumé des étapes des chantiers, calculé par un autre module.

    chantiers ne connaît pas le module étapes : la composition root branche ce
    port sur le cas d'usage public `CalculerResumesEtapes` d'étapes, au travers d'un
    petit adaptateur qui traduit sa vue en `ResumeEtapes`. La dépendance est ainsi
    inversée, et il n'y a pas d'import circulaire (intent.md, §2.3).
    """

    def executer(self, chantier_ids: Sequence[UUID]) -> Mapping[UUID, ResumeEtapes]:
        """Renvoie le résumé de chaque chantier demandé ; un chantier sans étape a un résumé nul."""
        ...
