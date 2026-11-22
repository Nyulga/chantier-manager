"""Repository mémoire des chantiers, utilisé par les tests des cas d'usage."""

from uuid import UUID

from app.chantiers.domain.chantier import Chantier
from app.shared.domain.erreurs import NonTrouveError
from app.shared.infrastructure.memoire.unit_of_work import MemoireEntrepot


class MemoireChantierRepository(MemoireEntrepot[Chantier]):
    """Implémentation mémoire de `ChantierRepository`, annulable par sa Unit of Work."""

    def ajouter(self, chantier: Chantier) -> None:
        """Enregistre le chantier sous son identifiant."""
        self.elements[chantier.id] = chantier

    def obtenir(self, chantier_id: UUID) -> Chantier:
        """Renvoie le chantier enregistré sous cet identifiant.

        Lève :
            NonTrouveError : aucun chantier n'a cet identifiant.
        """
        try:
            return self.elements[chantier_id]
        except KeyError:
            raise NonTrouveError("Chantier introuvable.") from None

    def lister(self) -> list[Chantier]:
        """Renvoie les chantiers triés par identifiant, donc par ordre de création (UUID v7)."""
        return sorted(self.elements.values(), key=lambda chantier: chantier.id)
