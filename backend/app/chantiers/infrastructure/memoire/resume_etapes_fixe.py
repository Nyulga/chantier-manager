"""Fournisseur de résumés d'étapes aux valeurs fixées par le test.

Il remplace le calcul du module étapes dans les tests de chantiers, qui n'ont pas
à connaître ce module.
"""

from collections.abc import Mapping, Sequence
from uuid import UUID

from app.chantiers.application.ports import RESUME_SANS_ETAPE, ResumeEtapesChantier


class ResumeEtapesFixe:
    """Implémentation de `FournisseurResumeEtapes` qui renvoie des résumés connus d'avance.

    Un chantier absent des valeurs fixées a le résumé d'un chantier sans étape.
    """

    def __init__(self, resumes: Mapping[UUID, ResumeEtapesChantier]) -> None:
        self._resumes = resumes

    def executer(self, chantier_ids: Sequence[UUID]) -> Mapping[UUID, ResumeEtapesChantier]:
        """Renvoie le résumé fixé de chaque chantier demandé."""
        return {
            chantier_id: self._resumes.get(chantier_id, RESUME_SANS_ETAPE)
            for chantier_id in chantier_ids
        }
