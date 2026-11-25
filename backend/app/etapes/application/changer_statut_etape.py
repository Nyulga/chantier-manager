"""Cas d'usage : faire avancer, valider ou refuser une étape."""

from dataclasses import dataclass
from uuid import UUID

from app.etapes.application.plafonds import (
    LIMITE_TRANSITIONS_PAR_ETAPE,
    MESSAGE_LIMITE_TRANSITIONS,
)
from app.etapes.application.ports import UnitOfWorkEtapes
from app.etapes.application.vues import EtapeVue, vue_etape
from app.etapes.domain.cycle import lire_action, mene_a_un_statut_final
from app.shared.application.plafond import exiger_place_sous_le_plafond
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

    Le plafond de la démo (`LIMITE_TRANSITIONS_PAR_ETAPE`) est vérifié ensuite, avant
    la transition et donc avant toute écriture. Il est vérifié ici, et non dans chaque
    action, parce que toutes les transitions passent par ce cas d'usage. Il vient après
    le chargement de l'étape, pour qu'une étape inconnue reste inconnue, et après la
    version, pour que l'acteur apprenne d'abord à recharger. Il précède aussi le
    contrôle du cycle : une étape pleine refuse toute action qui la fait boucler,
    permise ou non. Son historique est déjà chargé avec elle : le nombre d'entrées
    sert au plafond sans seconde lecture, et cette lecture reste légère puisque le
    plafond la borne.

    La validation échappe au plafond, parce qu'elle mène à un statut final (règle du
    domaine, `mene_a_un_statut_final`). Elle ne peut donc arriver qu'une fois et ne
    fait pas grossir l'historique sans limite : 21 entrées au plus. Sans cette
    exemption, une étape remplie par des refus resterait à vie « À valider », et son
    chantier ne pourrait plus atteindre 100 %. Le cycle s'applique toujours : un
    ouvrier qui tente de valider une étape pleine reçoit `AccesRefuseError`.

    Lève :
        ValeurInvalideError : l'action est inconnue, ou le commentaire est absent alors
            qu'il est obligatoire, ou trop long.
        NonTrouveError : l'étape n'existe pas.
        ConflitVersionError : l'étape a changé depuis la version attendue, ou une autre
            transaction l'a modifiée en même temps.
        PlafondAtteintError : l'étape a déjà `LIMITE_TRANSITIONS_PAR_ETAPE` transitions,
            et l'action n'est pas la validation.
        AccesRefuseError : ce rôle n'a droit à cette action depuis aucun statut (un
            ouvrier qui valide ou refuse).
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
            if not mene_a_un_statut_final(action):
                exiger_place_sous_le_plafond(
                    len(etape.historique), LIMITE_TRANSITIONS_PAR_ETAPE, MESSAGE_LIMITE_TRANSITIONS
                )
            etape.appliquer(action, acteur, self._horloge.maintenant(), commande.commentaire)
            vue = vue_etape(etape, acteur)
            self._uow.valider()
        return vue
