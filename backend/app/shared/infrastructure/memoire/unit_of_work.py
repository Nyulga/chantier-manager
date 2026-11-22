"""Unit of Work en mémoire, et le stockage mémoire qu'elle sait annuler.

Les fakes de chaque module s'appuient sur ces deux classes : elles leur donnent la
même sémantique transactionnelle que l'implémentation SQL (règle 03, principe L),
sans réécrire l'annulation dans chaque module.
"""

import copy
from types import TracebackType
from typing import Protocol, Self
from uuid import UUID


class Annulable(Protocol):
    """Ce que l'Unit of Work mémoire attend d'un stockage : capturer puis restaurer."""

    def capturer(self) -> None:
        """Mémorise l'état courant, au début d'une transaction."""
        ...

    def restaurer(self) -> None:
        """Revient à l'état mémorisé, quand la transaction est annulée."""
        ...


class MemoireEntrepot[T]:
    """Stockage mémoire d'objets indexés par identifiant, que l'on peut annuler.

    La capture est une copie profonde : les entités sont modifiées sur place par le
    domaine, et une copie superficielle ne permettrait pas de revenir en arrière.
    """

    def __init__(self) -> None:
        self.elements: dict[UUID, T] = {}
        self._capture: dict[UUID, T] = {}

    def capturer(self) -> None:
        """Mémorise une copie indépendante de l'état courant."""
        self._capture = copy.deepcopy(self.elements)

    def restaurer(self) -> None:
        """Remplace l'état courant par la copie mémorisée au début de la transaction."""
        self.elements = self._capture


class MemoireUnitOfWork:
    """Unit of Work mémoire : implémente le port `UnitOfWork` pour les tests.

    Sortir du bloc `with` sans avoir appelé `valider()`, en particulier à cause
    d'une exception, restaure les stockages dans leur état d'entrée. Le compteur
    `validations` permet aux tests de vérifier qu'un cas d'usage valide une seule
    fois, ou pas du tout en cas d'échec.
    """

    def __init__(self, *entrepots: Annulable) -> None:
        self._entrepots = entrepots
        self._validee = False
        self.validations = 0

    def __enter__(self) -> Self:
        """Ouvre la transaction : chaque stockage mémorise son état."""
        self._validee = False
        for entrepot in self._entrepots:
            entrepot.capturer()
        return self

    def __exit__(
        self,
        type_erreur: type[BaseException] | None,
        erreur: BaseException | None,
        trace: TracebackType | None,
    ) -> None:
        """Ferme la transaction, en l'annulant si elle n'a pas été validée.

        L'exception éventuelle n'est pas absorbée : elle remonte à l'appelant.
        """
        if self._validee:
            return
        for entrepot in self._entrepots:
            entrepot.restaurer()

    def valider(self) -> None:
        """Valide la transaction : les écritures seront conservées à la sortie du bloc."""
        self._validee = True
        self.validations += 1
