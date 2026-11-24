"""Routes des étapes : traduisent HTTP en appels de cas d'usage, sans logique métier."""

from http import HTTPStatus
from typing import Annotated, Protocol
from uuid import UUID

from fastapi import APIRouter, Depends, params

from app.etapes.api.capacites import CasUsagesCapacites, creer_routeur_capacites
from app.etapes.api.conversions import (
    commande_ajout_depuis,
    commande_statut_depuis,
    reponse_depuis,
)
from app.etapes.api.schemas import AjouterEtapeRequete, EtapeReponse, TransitionRequete
from app.etapes.api.tableau_de_bord import CasUsagesTableauDeBord, creer_routeur_tableau_de_bord
from app.etapes.application.ajouter_etape import AjouterEtape
from app.etapes.application.changer_statut_etape import ChangerStatutEtape
from app.etapes.application.lister_etapes import ListerEtapes
from app.shared.api.acteur import ActeurCourant
from app.shared.api.champ_piege import dependances_champ_piege
from app.shared.api.documentation_erreurs import erreurs_documentees
from app.shared.application.ports import ListeAdressesBloquees

# Les erreurs possibles, documentées dans OpenAPI pour le client généré. Leur corps
# est celui de la traduction centrale (RFC 9457).
ERREURS = erreurs_documentees(
    HTTPStatus.BAD_REQUEST,
    HTTPStatus.FORBIDDEN,
    HTTPStatus.NOT_FOUND,
    HTTPStatus.CONFLICT,
    HTTPStatus.UNPROCESSABLE_ENTITY,
    HTTPStatus.SERVICE_UNAVAILABLE,
)


class CasUsagesEtapes(CasUsagesTableauDeBord, CasUsagesCapacites, Protocol):
    """Ce que les routes demandent à la composition root : des cas d'usage prêts à l'emploi.

    Les cas d'usage du tableau de bord et des capacités sont déclarés avec leurs routes,
    dans `tableau_de_bord.py` et `capacites.py`.
    """

    def lister_etapes(self) -> ListerEtapes:
        """Fournit le cas d'usage de liste."""
        ...

    def ajouter_etape(self) -> AjouterEtape:
        """Fournit le cas d'usage d'ajout."""
        ...

    def changer_statut_etape(self) -> ChangerStatutEtape:
        """Fournit le cas d'usage de changement de statut."""
        ...


def creer_routeur(
    cas_usages: CasUsagesEtapes, adresses_bloquees: ListeAdressesBloquees
) -> APIRouter:
    """Crée le routeur des étapes, branché sur les cas d'usage et la liste des pièges."""
    routeur = APIRouter()
    # En premier : les routes sont essayées dans l'ordre, et `/etapes/a-valider` ne doit
    # jamais être lu comme un `/etapes/{etape_id}` (voir test_ordre_des_routes.py).
    routeur.include_router(creer_routeur_tableau_de_bord(cas_usages))
    routeur.include_router(creer_routeur_capacites(cas_usages))
    routeur.include_router(
        _creer_routeur_etapes_du_chantier(cas_usages, dependances_champ_piege(adresses_bloquees))
    )
    routeur.include_router(_creer_routeur_transitions(cas_usages))
    return routeur


def _creer_routeur_etapes_du_chantier(
    cas_usages: CasUsagesEtapes, gardes: list[params.Depends]
) -> APIRouter:
    """Crée les routes qui lisent les étapes d'un chantier et en ajoutent."""
    routeur = APIRouter(tags=["étapes"], responses=ERREURS)

    @routeur.get(
        "/chantiers/{chantier_id}/etapes",
        status_code=HTTPStatus.OK,
        response_model=list[EtapeReponse],
        summary="Liste les étapes d'un chantier",
    )
    def lister(
        chantier_id: UUID,
        acteur: ActeurCourant,
        cas_usage: Annotated[ListerEtapes, Depends(cas_usages.lister_etapes)],
    ) -> list[EtapeReponse]:
        return [reponse_depuis(vue) for vue in cas_usage.executer(chantier_id, acteur)]

    @routeur.post(
        "/chantiers/{chantier_id}/etapes",
        status_code=HTTPStatus.CREATED,
        response_model=EtapeReponse,
        summary="Ajoute une étape en fin de liste",
        dependencies=gardes,
    )
    def ajouter(
        chantier_id: UUID,
        requete: AjouterEtapeRequete,
        acteur: ActeurCourant,
        cas_usage: Annotated[AjouterEtape, Depends(cas_usages.ajouter_etape)],
    ) -> EtapeReponse:
        commande = commande_ajout_depuis(chantier_id, requete)
        return reponse_depuis(cas_usage.executer(commande, acteur))

    return routeur


def _creer_routeur_transitions(cas_usages: CasUsagesEtapes) -> APIRouter:
    """Crée la route qui fait avancer, valide ou refuse une étape."""
    routeur = APIRouter(tags=["étapes"], responses=ERREURS)

    @routeur.post(
        "/etapes/{etape_id}/transitions",
        status_code=HTTPStatus.OK,
        response_model=EtapeReponse,
        summary="Fait avancer, valide ou refuse",
    )
    def changer_statut(
        etape_id: UUID,
        requete: TransitionRequete,
        acteur: ActeurCourant,
        cas_usage: Annotated[ChangerStatutEtape, Depends(cas_usages.changer_statut_etape)],
    ) -> EtapeReponse:
        commande = commande_statut_depuis(etape_id, requete)
        return reponse_depuis(cas_usage.executer(commande, acteur))

    return routeur
