"""Cas d'usage public : vérifier qu'un chantier existe, pour le compte d'un autre module."""

from uuid import UUID

from app.chantiers.application.ports import UnitOfWorkChantiers


class VerifierChantierExiste:
    """Vérifie qu'un chantier existe ; utilisé par étapes avant de lister ses étapes.

    Il ne prend pas d'acteur : dans le squelette, l'existence suffit, car tout
    chantier est visible. En phase 2, il deviendra la vérification d'affectation.

    Lève :
        NonTrouveError : le chantier n'existe pas.
    """

    def __init__(self, uow: UnitOfWorkChantiers) -> None:
        self._uow = uow

    def executer(self, chantier_id: UUID) -> None:
        """Ne renvoie rien si le chantier existe ; lève `NonTrouveError` sinon."""
        with self._uow:
            self._uow.chantiers.obtenir(chantier_id)
