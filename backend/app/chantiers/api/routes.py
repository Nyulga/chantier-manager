"""Routes des chantiers : traduisent HTTP en appels de cas d'usage, sans logique métier."""

from http import HTTPStatus
from typing import Annotated, Protocol
from uuid import UUID

from fastapi import APIRouter, Depends, params

from app.chantiers.api.conversions import commande_depuis, reponse_depuis
from app.chantiers.api.schemas import ChantierReponse, CreerChantierRequete
from app.chantiers.application.consulter_chantier import ConsulterChantier
from app.chantiers.application.creer_chantier import CreerChantier
from app.chantiers.application.lister_chantiers import ListerChantiers
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


class CasUsagesChantiers(Protocol):
    """Ce que les routes demandent à la composition root : des cas d'usage prêts à l'emploi.

    Les routes ne connaissent ni l'infrastructure ni la composition : celle-ci leur
    est transmise à la création du routeur, ce qui garde `chantiers` indépendant de `etapes`.
    """

    def creer_chantier(self) -> CreerChantier:
        """Fournit le cas d'usage de création."""
        ...

    def lister_chantiers(self) -> ListerChantiers:
        """Fournit le cas d'usage de liste."""
        ...

    def consulter_chantier(self) -> ConsulterChantier:
        """Fournit le cas d'usage de consultation."""
        ...


def creer_routeur(
    cas_usages: CasUsagesChantiers, adresses_bloquees: ListeAdressesBloquees | None = None
) -> APIRouter:
    """Crée le routeur des chantiers, branché sur les cas d'usage et la liste des pièges."""
    routeur = APIRouter(prefix="/chantiers", tags=["chantiers"], responses=ERREURS)
    _declarer_creation(routeur, cas_usages, dependances_champ_piege(adresses_bloquees))
    _declarer_lectures(routeur, cas_usages)
    return routeur


def _declarer_creation(
    routeur: APIRouter, cas_usages: CasUsagesChantiers, gardes: list[params.Depends]
) -> None:
    @routeur.post(
        "",
        status_code=HTTPStatus.CREATED,
        response_model=ChantierReponse,
        summary="Crée un chantier",
        dependencies=gardes,
    )
    def creer(
        requete: CreerChantierRequete,
        acteur: ActeurCourant,
        cas_usage: Annotated[CreerChantier, Depends(cas_usages.creer_chantier)],
    ) -> ChantierReponse:
        return reponse_depuis(cas_usage.executer(commande_depuis(requete), acteur))


def _declarer_lectures(routeur: APIRouter, cas_usages: CasUsagesChantiers) -> None:
    @routeur.get(
        "",
        status_code=HTTPStatus.OK,
        response_model=list[ChantierReponse],
        summary="Liste les chantiers, avec leur avancement",
    )
    def lister(
        acteur: ActeurCourant,
        cas_usage: Annotated[ListerChantiers, Depends(cas_usages.lister_chantiers)],
    ) -> list[ChantierReponse]:
        return [reponse_depuis(vue) for vue in cas_usage.executer(acteur)]

    @routeur.get(
        "/{chantier_id}",
        status_code=HTTPStatus.OK,
        response_model=ChantierReponse,
        summary="Consulte un chantier",
    )
    def consulter(
        chantier_id: UUID,
        acteur: ActeurCourant,
        cas_usage: Annotated[ConsulterChantier, Depends(cas_usages.consulter_chantier)],
    ) -> ChantierReponse:
        return reponse_depuis(cas_usage.executer(chantier_id, acteur))
