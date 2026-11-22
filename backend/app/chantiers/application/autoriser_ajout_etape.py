"""Cas d'usage public : vérifier qu'un acteur peut ajouter une étape à un chantier."""

from uuid import UUID

from app.chantiers.application.ports import UnitOfWorkChantiers
from app.chantiers.domain.politiques import peut_ajouter_etape
from app.shared.domain.acteur import Acteur
from app.shared.domain.erreurs import AccesRefuseError


class AutoriserAjoutEtape:
    """Vérifie qu'un chantier existe et que l'acteur peut y ajouter une étape.

    Utilisé par étapes : la règle « seul un chef définit les étapes » porte sur le
    chantier, elle est donc décidée ici, une seule fois, et la vue du chantier en
    découle aussi (`peut_ajouter_etape`). L'existence est vérifiée en premier : un
    chantier inconnu donne `NonTrouveError` quel que soit le rôle.

    Lève :
        NonTrouveError : le chantier n'existe pas.
        AccesRefuseError : l'acteur n'a pas le droit d'ajouter une étape.
    """

    def __init__(self, uow: UnitOfWorkChantiers) -> None:
        self._uow = uow

    def executer(self, chantier_id: UUID, acteur: Acteur) -> None:
        """Ne renvoie rien si l'ajout est permis ; lève une erreur métier sinon."""
        with self._uow:
            self._uow.chantiers.obtenir(chantier_id)
        if not peut_ajouter_etape(acteur):
            raise AccesRefuseError("Seul un chef peut ajouter une étape à un chantier.")
