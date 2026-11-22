"""Cas d'usage : faire avancer, valider ou refuser une étape."""

from dataclasses import dataclass
from uuid import UUID

from app.etapes.application.ports import UnitOfWorkEtapes
from app.etapes.application.vues import EtapeVue, vue_etape
from app.etapes.domain.cycle import lire_action
from app.shared.application.ports import Horloge
from app.shared.domain.acteur import Acteur


@dataclass(frozen=True)
class ChangementStatut:
    """Commande de changement de statut.

    `action` est le nom d'une action du cycle (`"demarrer"`, `"signaler_terminee"`,
    `"valider"`, `"refuser"`) ; `commentaire` est obligatoire pour un refus.
    """

    etape_id: UUID
    action: str
    commentaire: str | None = None


class ChangerStatutEtape:
    """Applique une action du cycle à une étape, et enregistre la transition.

    Un seul cas d'usage couvre toutes les actions : la décision appartient à la
    table des transitions du domaine, et le déroulé est identique pour chacune.
    Ajouter une action au cycle ne demande donc qu'une ligne dans la table. Le
    changement de statut et son entrée d'historique sont enregistrés dans la même
    transaction : on ne voit jamais l'un sans l'autre.

    Lève :
        ValeurInvalideError : l'action est inconnue, ou un commentaire obligatoire manque.
        NonTrouveError : l'étape n'existe pas.
        TransitionInterditeError : l'action n'est pas permise à ce rôle dans l'état actuel.
    """

    def __init__(self, uow: UnitOfWorkEtapes, horloge: Horloge) -> None:
        self._uow = uow
        self._horloge = horloge

    def executer(self, commande: ChangementStatut, acteur: Acteur) -> EtapeVue:
        """Applique l'action et renvoie la nouvelle vue de l'étape pour l'acteur."""
        action = lire_action(commande.action)
        with self._uow:
            etape = self._uow.etapes.obtenir(commande.etape_id)
            etape.appliquer(action, acteur, self._horloge.maintenant(), commande.commentaire)
            vue = vue_etape(etape, acteur)
            self._uow.valider()
        return vue
