"""Générateur d'identifiants prévisibles, pour les tests."""

from uuid import UUID


class GenerateurIdPrevisible:
    """Implémentation du port `GenerateurId` qui renvoie les UUID 1, 2, 3, et ainsi de suite.

    Les identifiants sont croissants, comme les UUID v7 de production : un test qui
    dépend de l'ordre de création se comporte donc de la même façon.
    """

    def __init__(self) -> None:
        self._dernier = 0

    def nouveau(self) -> UUID:
        """Renvoie l'identifiant suivant, jamais encore distribué."""
        self._dernier += 1
        return UUID(int=self._dernier)
