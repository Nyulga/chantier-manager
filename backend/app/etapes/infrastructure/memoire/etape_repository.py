"""Repository mémoire des étapes, utilisé par les tests des cas d'usage."""

from collections.abc import Sequence
from uuid import UUID

from app.etapes.domain.cycle import StatutEtape
from app.etapes.domain.etape import Etape, HistoriqueEtape
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

    def lister_par_statut(self, statut: StatutEtape) -> list[Etape]:
        """Renvoie les étapes à ce statut, dans l'ordre de leur identifiant."""
        etapes = [etape for etape in self.elements.values() if etape.statut is statut]
        return sorted(etapes, key=lambda etape: etape.id)

    def lister_dernieres_transitions(self, limite: int) -> list[tuple[Etape, HistoriqueEtape]]:
        """Renvoie les `limite` entrées d'historique les plus récentes, avec leur étape.

        L'historique de chaque étape est parcouru à rebours, puis le tout est trié
        par date décroissante. Le tri de Python est stable, y compris en ordre
        inverse : à date égale, l'entrée la plus récente d'une étape reste devant.
        """
        entrees = [
            (etape, entree)
            for etape in sorted(self.elements.values(), key=lambda etape: etape.id)
            for entree in reversed(etape.historique)
        ]
        entrees.sort(key=lambda paire: paire[1].date, reverse=True)
        return entrees[:limite]
