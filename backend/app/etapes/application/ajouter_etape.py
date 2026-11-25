"""Cas d'usage : ajouter une étape à la fin de la liste d'un chantier."""

from dataclasses import dataclass
from uuid import UUID

from app.etapes.application.plafonds import LIMITE_ETAPES_PAR_CHANTIER, MESSAGE_LIMITE_ETAPES
from app.etapes.application.ports import AutorisationAjoutEtape, UnitOfWorkEtapes
from app.etapes.application.vues import EtapeVue, vue_etape
from app.etapes.domain.etape import Etape, ordre_suivant
from app.shared.application.plafond import exiger_place_sous_le_plafond
from app.shared.application.ports import GenerateurId
from app.shared.domain.acteur import Acteur


@dataclass(frozen=True)
class NouvelleEtape:
    """Commande d'ajout d'une étape à un chantier."""

    chantier_id: UUID
    titre: str


class AjouterEtape:
    """Ajoute une étape « À faire » à la fin de la liste d'un chantier.

    Le droit est demandé au module chantiers, qui le décide (`AutorisationAjoutEtape`),
    avant d'ouvrir la transaction des étapes.

    Le plafond de la démo (`LIMITE_ETAPES_PAR_CHANTIER`) est vérifié ensuite, dans la
    transaction de l'ajout et avant toute écriture. Il passe après le droit et
    l'existence du chantier : un ouvrier reçoit son refus de droit, et un chantier
    inconnu reste inconnu, sans que le plafond renseigne sur ses étapes. Les étapes du
    chantier sont déjà lues pour calculer l'ordre de la nouvelle : leur nombre sert au
    plafond, sans seconde lecture. Cette lecture complète reste légère parce que ce
    même plafond la borne à 30 étapes ; s'il montait, un comptage par la base serait à
    ajouter au port, avec ses implémentations (`dev-donnees`).

    Lève :
        NonTrouveError : le chantier n'existe pas.
        AccesRefuseError : l'acteur n'a pas le droit d'ajouter une étape.
        PlafondAtteintError : le chantier a déjà `LIMITE_ETAPES_PAR_CHANTIER` étapes.
        ValeurInvalideError : le titre est vide, trop long ou contient un caractère interdit.
        ConflitVersionError : une autre étape a pris le même rang entre-temps.
    """

    def __init__(
        self,
        uow: UnitOfWorkEtapes,
        generateur_id: GenerateurId,
        autorisation: AutorisationAjoutEtape,
    ) -> None:
        self._uow = uow
        self._generateur_id = generateur_id
        self._autorisation = autorisation

    def executer(self, commande: NouvelleEtape, acteur: Acteur) -> EtapeVue:
        """Ajoute l'étape et renvoie sa vue pour l'acteur."""
        self._autorisation.executer(commande.chantier_id, acteur)
        with self._uow:
            existantes = self._uow.etapes.lister_par_chantiers([commande.chantier_id])
            exiger_place_sous_le_plafond(
                len(existantes), LIMITE_ETAPES_PAR_CHANTIER, MESSAGE_LIMITE_ETAPES
            )
            etape = Etape.creer(
                self._generateur_id.nouveau(),
                commande.chantier_id,
                commande.titre,
                ordre_suivant(existantes),
            )
            self._uow.etapes.ajouter(etape)
            vue = vue_etape(etape, acteur)
            self._uow.valider()
        return vue
