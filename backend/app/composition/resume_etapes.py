"""Adaptateur entre le résumé publié par étapes et le port de chantiers qui l'attend."""

from collections.abc import Sequence
from uuid import UUID

from app.chantiers.application.ports import ResumeEtapes
from app.etapes.application import CalculerResumesEtapes


class ResumeEtapesDepuisEtapes:
    """Implémente `FournisseurResumeEtapes` (chantiers) avec `CalculerResumesEtapes` (étapes).

    Les deux modules s'ignorent (contrat import-linter `chantiers-sans-etapes`) :
    chacun a donc son propre type de résumé, et seule la composition root, qui
    connaît les deux, recopie l'un dans l'autre.
    """

    def __init__(self, calcul: CalculerResumesEtapes) -> None:
        self._calcul = calcul

    def executer(self, chantier_ids: Sequence[UUID]) -> dict[UUID, ResumeEtapes]:
        """Renvoie le résumé de chaque chantier demandé, dans le type de chantiers."""
        return {
            chantier_id: ResumeEtapes(
                avancement=resume.avancement,
                validees=resume.validees,
                total=resume.total,
                a_valider=resume.a_valider,
            )
            for chantier_id, resume in self._calcul.executer(chantier_ids).items()
        }
