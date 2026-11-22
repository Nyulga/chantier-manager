"""Repository SQL des étapes."""

from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.etapes.domain.etape import Etape
from app.etapes.infrastructure.sql.tables import TABLE_ETAPES
from app.shared.domain.erreurs import NonTrouveError


class SqlEtapeRepository:
    """Implémentation SQL de `EtapeRepository`, liée à la session d'une transaction.

    Une étape chargée puis modifiée est enregistrée à la validation de la transaction
    (la session suit ses changements). Il n'appelle jamais `commit`.
    """

    def __init__(self, session: Session) -> None:
        self._session = session

    def ajouter(self, etape: Etape) -> None:
        """Enregistre l'étape, et son historique, dans la transaction en cours."""
        self._session.add(etape)

    def obtenir(self, etape_id: UUID) -> Etape:
        """Charge l'étape avec son historique.

        Lève :
            NonTrouveError : aucune étape n'a cet identifiant.
        """
        etape = self._session.get(Etape, etape_id)
        if etape is None:
            raise NonTrouveError("Étape introuvable.")
        return etape

    def lister_par_chantiers(self, chantier_ids: Sequence[UUID]) -> list[Etape]:
        """Renvoie les étapes de ces chantiers, triées par ordre, en une seule lecture.

        L'historique est chargé par une seconde requête groupée (`lazy="selectin"`).
        """
        requete = (
            select(Etape)
            .where(TABLE_ETAPES.c.chantier_id.in_(chantier_ids))
            .order_by(TABLE_ETAPES.c.ordre, TABLE_ETAPES.c.id)
        )
        return list(self._session.scalars(requete))
