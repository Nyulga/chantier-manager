"""Espion de test : vérifie que le résumé des étapes est demandé hors de la transaction."""

from collections.abc import Mapping, Sequence
from uuid import UUID

from app.chantiers.application.ports import RESUME_SANS_ETAPE, ResumeEtapesChantier
from app.chantiers.infrastructure.memoire.unit_of_work import MemoireUnitOfWorkChantiers


class ResumeEtapesEspion:
    """Fournisseur de résumés nuls qui note si la transaction des chantiers était ouverte.

    Le calcul réel ouvre sa propre transaction sur les étapes : l'appeler pendant celle
    des chantiers tiendrait deux connexions à la fois pour une seule requête.
    """

    def __init__(self, uow: MemoireUnitOfWorkChantiers) -> None:
        self._uow = uow
        self.appele_en_transaction: list[bool] = []

    def executer(self, chantier_ids: Sequence[UUID]) -> Mapping[UUID, ResumeEtapesChantier]:
        """Note l'état de la transaction, puis renvoie un résumé nul pour chaque chantier."""
        self.appele_en_transaction.append(self._uow.ouverte)
        return dict.fromkeys(chantier_ids, RESUME_SANS_ETAPE)
