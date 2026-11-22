"""Cas d'usage public : résumer les étapes de plusieurs chantiers à la fois."""

from collections.abc import Sequence
from uuid import UUID

from app.etapes.application.ports import UnitOfWorkEtapes
from app.etapes.application.vues import ResumeEtapesVue, vue_resume
from app.etapes.domain.avancement import resumer_etapes


class CalculerResumesEtapes:
    """Résume les étapes de chaque chantier demandé : compteurs et avancement.

    La composition root le branche, par un adaptateur, sur le port
    `FournisseurResumeEtapes` de chantiers. Les étapes de tous les chantiers sont
    lues en une seule fois, pour que la liste des chantiers ne fasse pas une lecture
    par chantier. Il ne prend pas d'acteur : c'est le cas d'usage de chantiers qui
    l'appelle qui a vérifié les droits.
    """

    def __init__(self, uow: UnitOfWorkEtapes) -> None:
        self._uow = uow

    def executer(self, chantier_ids: Sequence[UUID]) -> dict[UUID, ResumeEtapesVue]:
        """Renvoie un résumé par chantier demandé ; il est nul pour un chantier sans étape."""
        with self._uow:
            etapes = self._uow.etapes.lister_par_chantiers(chantier_ids)
        return {
            chantier_id: vue_resume(
                resumer_etapes([etape for etape in etapes if etape.chantier_id == chantier_id])
            )
            for chantier_id in chantier_ids
        }
