"""Cas d'usage public : calculer l'avancement de plusieurs chantiers à la fois."""

from collections.abc import Sequence
from uuid import UUID

from app.etapes.application.ports import UnitOfWorkEtapes
from app.etapes.domain.avancement import calculer_avancement


class CalculerAvancements:
    """Calcule l'avancement de chaque chantier demandé, à partir de ses étapes.

    La composition root le branche sur le port `FournisseurAvancement` de chantiers.
    Les étapes de tous les chantiers sont lues en une seule fois, pour que la liste
    des chantiers ne fasse pas une lecture par chantier. Il ne prend pas d'acteur :
    c'est le cas d'usage de chantiers qui l'appelle qui a vérifié les droits.
    """

    def __init__(self, uow: UnitOfWorkEtapes) -> None:
        self._uow = uow

    def executer(self, chantier_ids: Sequence[UUID]) -> dict[UUID, int]:
        """Renvoie un pourcentage de 0 à 100 par chantier demandé ; 0 s'il n'a pas d'étape."""
        with self._uow:
            etapes = self._uow.etapes.lister_par_chantiers(chantier_ids)
        return {
            chantier_id: calculer_avancement(
                [etape for etape in etapes if etape.chantier_id == chantier_id]
            )
            for chantier_id in chantier_ids
        }
