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
    `"valider"`, `"refuser"`). `commentaire` est facultatif sur toute action, et
    obligatoire pour un refus. `version_attendue` est la version de l'étape que
    l'acteur avait sous les yeux : si elle est donnée et que l'étape a changé
    depuis, l'action est rejetée. Sans elle, seul le verrou de la transaction joue.
    """

    etape_id: UUID
    action: str
    commentaire: str | None = None
    version_attendue: int | None = None


class ChangerStatutEtape:
    """Applique une action du cycle à une étape, et enregistre la transition.

    Un seul cas d'usage couvre toutes les actions : la décision appartient à la
    table des transitions du domaine, et le déroulé est identique pour chacune.
    Ajouter une action au cycle ne demande donc qu'une ligne dans la table. Le
    changement de statut et son entrée d'historique sont enregistrés dans la même
    transaction : on ne voit jamais l'un sans l'autre.

    La version attendue est vérifiée avant la transition : une action décidée sur
    un état périmé est un conflit (409), même si elle serait aussi interdite dans
    l'état actuel. C'est ce que l'acteur doit apprendre en premier : recharger.

    Lève :
        ValeurInvalideError : l'action est inconnue, ou le commentaire est absent alors
            qu'il est obligatoire, ou trop long.
        NonTrouveError : l'étape n'existe pas.
        ConflitVersionError : l'étape a changé depuis la version attendue, ou une autre
            transaction l'a modifiée en même temps.
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
            etape.verifier_version(commande.version_attendue)
            etape.appliquer(action, acteur, self._horloge.maintenant(), commande.commentaire)
            vue = vue_etape(etape, acteur)
            self._uow.valider()
        return vue
