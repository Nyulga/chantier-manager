"""Ports du module étapes : son repository, sa transaction et ce qu'il demande à chantiers."""

from collections.abc import Sequence
from typing import Protocol
from uuid import UUID

from app.etapes.domain.etape import Etape, HistoriqueEtape
from app.shared.application.ports import UnitOfWork
from app.shared.domain.acteur import Acteur


class EtapeRepository(Protocol):
    """Charge et enregistre des étapes complètes, historique compris.

    Il n'a pas de méthode « enregistrer » : une étape chargée puis modifiée dans une
    transaction est enregistrée à sa validation, comme le fait la session SQLAlchemy.
    """

    def ajouter(self, etape: Etape) -> None:
        """Enregistre une nouvelle étape dans la transaction en cours."""
        ...

    def obtenir(self, etape_id: UUID) -> Etape:
        """Charge une étape et son historique.

        Lève :
            NonTrouveError : aucune étape n'a cet identifiant.
        """
        ...

    def lister_par_chantiers(self, chantier_ids: Sequence[UUID]) -> list[Etape]:
        """Renvoie les étapes de ces chantiers, triées par ordre, en une seule lecture."""
        ...

    def lister_a_valider(self, limite: int) -> list[Etape]:
        """Renvoie au plus `limite` étapes « Terminée (à valider) », historique compris.

        Ce sont celles que `trier_par_signalement` placerait en tête, tous chantiers
        confondus : d'abord celles sans signalement connu, puis les plus anciennement
        signalées, puis le plus petit identifiant à date égale. La sélection doit
        donc suivre la règle du domaine ; l'ordre de la liste, lui, n'est pas
        garanti, et le cas d'usage applique le tri du domaine.
        """
        ...

    def lister_dernieres_transitions(self, limite: int) -> list[tuple[Etape, HistoriqueEtape]]:
        """Renvoie au plus `limite` entrées d'historique, toutes étapes confondues.

        Elles vont de la plus récente à la plus ancienne, chacune avec l'étape qui
        la porte. À date égale, l'entrée la plus récemment ajoutée à une même étape
        vient en premier ; entre deux étapes différentes, l'ordre n'est pas garanti.
        La limite est déjà validée par le cas d'usage (`LimiteActivite`).
        """
        ...


class UnitOfWorkEtapes(UnitOfWork, Protocol):
    """Transaction du module étapes, qui donne accès à son repository."""

    @property
    def etapes(self) -> EtapeRepository:
        """Le repository des étapes, lié à la transaction en cours."""
        ...


class VerificationChantier(Protocol):
    """Vérifie qu'un chantier existe ; branché sur `VerifierChantierExiste` de chantiers.

    Le port est déclaré ici, du côté de celui qui en a besoin : étapes n'importe
    rien de chantiers, et la composition root fait le branchement.
    """

    def executer(self, chantier_id: UUID) -> None:
        """Lève `NonTrouveError` si le chantier n'existe pas."""
        ...


class DroitCreationChantier(Protocol):
    """Dit si un acteur peut créer un chantier ; branché sur `EvaluerCreationChantier`.

    Ce droit porte sur les chantiers, donc chantiers le décide : étapes ne fait que
    l'annoncer parmi les capacités de l'acteur (`ConsulterCapacites`).
    """

    def executer(self, acteur: Acteur) -> bool:
        """Renvoie vrai si l'acteur a le droit de créer un chantier."""
        ...


class AutorisationAjoutEtape(Protocol):
    """Vérifie qu'un acteur peut ajouter une étape ; branché sur `AutoriserAjoutEtape`.

    Ce droit porte sur le chantier, donc chantiers le décide : étapes ne le duplique pas.
    """

    def executer(self, chantier_id: UUID, acteur: Acteur) -> None:
        """Ne renvoie rien si l'ajout est permis.

        Lève :
            NonTrouveError : le chantier n'existe pas.
            AccesRefuseError : l'acteur n'a pas le droit d'ajouter une étape.
        """
        ...
