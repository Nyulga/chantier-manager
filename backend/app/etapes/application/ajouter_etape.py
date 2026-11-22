"""Cas d'usage : ajouter une étape à la fin de la liste d'un chantier."""

from dataclasses import dataclass
from uuid import UUID

from app.etapes.application.ports import AutorisationAjoutEtape, UnitOfWorkEtapes
from app.etapes.application.vues import EtapeVue, vue_etape
from app.etapes.domain.etape import Etape, ordre_suivant
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

    Lève :
        NonTrouveError : le chantier n'existe pas.
        AccesRefuseError : l'acteur n'a pas le droit d'ajouter une étape.
        ValeurInvalideError : le titre est vide.
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
