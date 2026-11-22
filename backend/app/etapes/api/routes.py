"""Routes des étapes : traduisent HTTP en appels de cas d'usage, sans logique métier."""

from http import HTTPStatus
from typing import Annotated, Any, Protocol
from uuid import UUID

from fastapi import APIRouter, Depends

from app.etapes.api.conversions import (
    commande_ajout_depuis,
    commande_statut_depuis,
    reponse_depuis,
)
from app.etapes.api.schemas import AjouterEtapeRequete, EtapeReponse, TransitionRequete
from app.etapes.application.ajouter_etape import AjouterEtape
from app.etapes.application.changer_statut_etape import ChangerStatutEtape
from app.etapes.application.lister_etapes import ListerEtapes
from app.shared.api.acteur import ActeurCourant

# Les erreurs possibles, documentées dans OpenAPI pour le client généré. Leur corps
# est celui de la traduction centrale (RFC 9457).
ERREURS: dict[int | str, dict[str, Any]] = {
    HTTPStatus.BAD_REQUEST: {"description": "Profil `X-Profil` absent ou inconnu."},
    HTTPStatus.FORBIDDEN: {"description": "Action réservée à un chef."},
    HTTPStatus.NOT_FOUND: {"description": "Chantier ou étape introuvable."},
    HTTPStatus.CONFLICT: {"description": "Transition impossible depuis l'état actuel."},
    HTTPStatus.UNPROCESSABLE_ENTITY: {"description": "Données invalides."},
}


class FournisseursEtapes(Protocol):
    """Ce que les routes demandent à la composition root : des cas d'usage prêts à l'emploi."""

    def lister_etapes(self) -> ListerEtapes:
        """Fournit le cas d'usage de liste."""
        ...

    def ajouter_etape(self) -> AjouterEtape:
        """Fournit le cas d'usage d'ajout."""
        ...

    def changer_statut_etape(self) -> ChangerStatutEtape:
        """Fournit le cas d'usage de changement de statut."""
        ...


def creer_routeur(fournisseurs: FournisseursEtapes) -> APIRouter:
    """Crée le routeur des étapes, branché sur les cas d'usage fournis."""
    routeur = APIRouter(tags=["étapes"], responses=ERREURS)

    @routeur.get("/chantiers/{chantier_id}/etapes", summary="Liste les étapes d'un chantier")
    def lister(
        chantier_id: UUID,
        acteur: ActeurCourant,
        cas_usage: Annotated[ListerEtapes, Depends(fournisseurs.lister_etapes)],
    ) -> list[EtapeReponse]:
        return [reponse_depuis(vue) for vue in cas_usage.executer(chantier_id, acteur)]

    @routeur.post(
        "/chantiers/{chantier_id}/etapes",
        status_code=HTTPStatus.CREATED,
        summary="Ajoute une étape en fin de liste",
    )
    def ajouter(
        chantier_id: UUID,
        requete: AjouterEtapeRequete,
        acteur: ActeurCourant,
        cas_usage: Annotated[AjouterEtape, Depends(fournisseurs.ajouter_etape)],
    ) -> EtapeReponse:
        commande = commande_ajout_depuis(chantier_id, requete)
        return reponse_depuis(cas_usage.executer(commande, acteur))

    @routeur.post("/etapes/{etape_id}/transitions", summary="Fait avancer, valide ou refuse")
    def changer_statut(
        etape_id: UUID,
        requete: TransitionRequete,
        acteur: ActeurCourant,
        cas_usage: Annotated[ChangerStatutEtape, Depends(fournisseurs.changer_statut_etape)],
    ) -> EtapeReponse:
        commande = commande_statut_depuis(etape_id, requete)
        return reponse_depuis(cas_usage.executer(commande, acteur))

    return routeur
