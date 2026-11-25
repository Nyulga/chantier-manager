"""Route des capacités : ce que l'acteur courant peut faire, sans logique métier."""

from http import HTTPStatus
from typing import Annotated, Protocol

from fastapi import APIRouter, Depends

from app.etapes.api.conversions import reponse_capacites_depuis
from app.etapes.api.schemas import CapacitesReponse
from app.etapes.application.consulter_capacites import ConsulterCapacites
from app.shared.api.acteur import ActeurCourant
from app.shared.api.documentation_erreurs import erreurs_documentees

# Le 422 est déclaré par cohérence : FastAPI en ajoute un, au corps non typé, à toute route
# qui lit un en-tête, et le client généré n'aurait alors pas la forme de l'erreur.
ERREURS = erreurs_documentees(
    HTTPStatus.BAD_REQUEST,
    HTTPStatus.UNPROCESSABLE_ENTITY,
    HTTPStatus.TOO_MANY_REQUESTS,
    HTTPStatus.SERVICE_UNAVAILABLE,
)


class CasUsagesCapacites(Protocol):
    """Le cas d'usage que la composition root fournit à la route des capacités."""

    def consulter_capacites(self) -> ConsulterCapacites:
        """Fournit le cas d'usage des capacités."""
        ...


def creer_routeur_capacites(cas_usages: CasUsagesCapacites) -> APIRouter:
    """Crée le routeur des capacités.

    La route vit dans le module étapes, qui porte déjà le tableau de bord et peut
    s'appuyer sur chantiers pour le droit de création (voir `ConsulterCapacites`).
    """
    routeur = APIRouter(tags=["profil"], responses=ERREURS)

    @routeur.get(
        "/moi",
        status_code=HTTPStatus.OK,
        response_model=CapacitesReponse,
        summary="Annonce ce que l'acteur courant peut faire",
    )
    def consulter(
        acteur: ActeurCourant,
        cas_usage: Annotated[ConsulterCapacites, Depends(cas_usages.consulter_capacites)],
    ) -> CapacitesReponse:
        return reponse_capacites_depuis(cas_usage.executer(acteur))

    return routeur
