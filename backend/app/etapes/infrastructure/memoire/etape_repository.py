"""Repository mémoire des étapes, utilisé par les tests des cas d'usage."""

from collections.abc import Sequence
from uuid import UUID

from app.etapes.domain.etape import Etape
from app.shared.domain.erreurs import NonTrouveError
from app.shared.infrastructure.memoire.unit_of_work import MemoireEntrepot


class MemoireEtapeRepository(MemoireEntrepot[Etape]):
    """Implémentation mémoire de `EtapeRepository`, annulable par sa Unit of Work."""

    def ajouter(self, etape: Etape) -> None:
        """Enregistre l'étape sous son identifiant."""
        self.elements[etape.id] = etape

    def obtenir(self, etape_id: UUID) -> Etape:
        """Renvoie l'étape enregistrée sous cet identifiant.

        Lève :
            NonTrouveError : aucune étape n'a cet identifiant.
        """
        try:
            return self.elements[etape_id]
        except KeyError:
            raise NonTrouveError("Étape introuvable.") from None

    def lister_par_chantiers(self, chantier_ids: Sequence[UUID]) -> list[Etape]:
        """Renvoie les étapes de ces chantiers, triées par ordre."""
        demandes = set(chantier_ids)
        etapes = [etape for etape in self.elements.values() if etape.chantier_id in demandes]
        return sorted(etapes, key=lambda etape: etape.ordre)
