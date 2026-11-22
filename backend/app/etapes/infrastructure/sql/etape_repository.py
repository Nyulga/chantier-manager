"""Repository SQL des étapes."""

from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.etapes.domain.cycle import StatutEtape
from app.etapes.domain.etape import Etape, HistoriqueEtape
from app.etapes.infrastructure.sql.tables import TABLE_ETAPES, TABLE_HISTORIQUE_ETAPES
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

    def lister_a_valider(self, limite: int) -> list[Etape]:
        """Renvoie au plus `limite` étapes à valider, celles qui attendent depuis le plus longtemps.

        La limite est appliquée par la base (`LIMIT`) : il faut donc que la base trie
        comme `trier_par_signalement`, sans quoi elle garderait d'autres étapes que
        celles que le domaine placerait en tête. La date de signalement est calculée
        comme `Etape.signalee_le` : la plus récente entrée d'historique vers
        « Terminée (à valider) », par une sous-requête groupée. Une étape sans
        signalement connu passe en tête (`NULLS FIRST`, explicite car PostgreSQL met
        les valeurs nulles en dernier), puis l'identifiant départage. L'historique
        complet est ensuite chargé par la requête groupée de `lazy="selectin"`.
        """
        historique = TABLE_HISTORIQUE_ETAPES.c
        signalements = (
            select(historique.etape_id, func.max(historique.date).label("signalee_le"))
            .where(historique.nouveau_statut == StatutEtape.TERMINEE_A_VALIDER)
            .group_by(historique.etape_id)
            .subquery()
        )
        requete = (
            select(Etape)
            .outerjoin(signalements, signalements.c.etape_id == TABLE_ETAPES.c.id)
            .where(TABLE_ETAPES.c.statut == StatutEtape.TERMINEE_A_VALIDER)
            .order_by(signalements.c.signalee_le.asc().nulls_first(), TABLE_ETAPES.c.id)
            .limit(limite)
        )
        return list(self._session.scalars(requete))

    def lister_dernieres_transitions(self, limite: int) -> list[tuple[Etape, HistoriqueEtape]]:
        """Renvoie au plus `limite` entrées d'historique, de la plus récente à la plus ancienne.

        La limite est appliquée par la base (`LIMIT`) : on ne charge jamais tout
        l'historique. La clé technique de l'entrée départage deux entrées de même
        date, comme l'ordre d'ajout. L'étape est lue dans la même requête (jointure),
        et son historique complet par la requête groupée de `lazy="selectin"` : deux
        requêtes au total, quel que soit le nombre d'entrées.
        """
        requete = (
            select(HistoriqueEtape, Etape)
            .join(Etape, TABLE_HISTORIQUE_ETAPES.c.etape_id == TABLE_ETAPES.c.id)
            .order_by(TABLE_HISTORIQUE_ETAPES.c.date.desc(), TABLE_HISTORIQUE_ETAPES.c.id.desc())
            .limit(limite)
        )
        return [(etape, entree) for entree, etape in self._session.execute(requete)]
