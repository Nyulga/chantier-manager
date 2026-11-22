"""Ports transverses : l'heure, les identifiants et la transaction.

Ce sont les seules sources non déterministes ou techniques dont les cas d'usage
ont besoin. Elles arrivent par le constructeur, ce qui permet de les remplacer
par des fakes dans les tests (règle 02).
"""

from datetime import datetime
from types import TracebackType
from typing import Protocol, Self
from uuid import UUID


class Horloge(Protocol):
    """Donne l'heure courante : le domaine ne lit jamais l'horloge du système lui-même."""

    def maintenant(self) -> datetime:
        """Renvoie l'instant présent, avec son fuseau horaire."""
        ...


class GenerateurId(Protocol):
    """Fournit les identifiants des nouveaux objets (UUID v7 en production, intent.md §2.3)."""

    def nouveau(self) -> UUID:
        """Renvoie un identifiant jamais encore attribué."""
        ...


class UnitOfWork(Protocol):
    """Transaction qui englobe tout un cas d'usage, utilisée comme gestionnaire de contexte.

    Les écritures ne sont conservées que si `valider()` a été appelée avant la
    sortie du bloc `with`. Toute sortie sans validation, en particulier à cause
    d'une exception, annule l'ensemble : on ne voit jamais un état à moitié écrit.
    Chaque module étend ce port pour y ajouter ses repositories.
    """

    def __enter__(self) -> Self:
        """Ouvre la transaction."""
        ...

    def __exit__(
        self,
        type_erreur: type[BaseException] | None,
        erreur: BaseException | None,
        trace: TracebackType | None,
    ) -> None:
        """Ferme la transaction, en l'annulant si elle n'a pas été validée."""
        ...

    def valider(self) -> None:
        """Valide la transaction ; un cas d'usage l'appelle une seule fois, à la fin."""
        ...
