"""Repository SQL des chantiers."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.chantiers.domain.chantier import Chantier
from app.chantiers.infrastructure.sql.tables import TABLE_CHANTIERS
from app.shared.domain.erreurs import NonTrouveError


class SqlChantierRepository:
    """Implémentation SQL de `ChantierRepository`, liée à la session d'une transaction.

    Il n'appelle jamais `commit` : c'est le rôle exclusif de l'Unit of Work.
    """

    def __init__(self, session: Session) -> None:
        self._session = session

    def ajouter(self, chantier: Chantier) -> None:
        """Enregistre le chantier dans la transaction en cours."""
        self._session.add(chantier)

    def obtenir(self, chantier_id: UUID) -> Chantier:
        """Charge le chantier.

        Lève :
            NonTrouveError : aucun chantier n'a cet identifiant.
        """
        chantier = self._session.get(Chantier, chantier_id)
        if chantier is None:
            raise NonTrouveError("Chantier introuvable.")
        return chantier

    def lister(self) -> list[Chantier]:
        """Renvoie les chantiers triés par identifiant, donc par ordre de création (UUID v7)."""
        requete = select(Chantier).order_by(TABLE_CHANTIERS.c.id)
        return list(self._session.scalars(requete))
