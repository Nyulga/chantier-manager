"""Routes des chantiers : traduisent HTTP en appels de cas d'usage, sans logique métier."""

from http import HTTPStatus
from typing import Annotated, Any, Protocol
from uuid import UUID

from fastapi import APIRouter, Depends

from app.chantiers.api.conversions import commande_depuis, reponse_depuis
from app.chantiers.api.schemas import ChantierReponse, CreerChantierRequete
from app.chantiers.application.consulter_chantier import ConsulterChantier
from app.chantiers.application.creer_chantier import CreerChantier
from app.chantiers.application.lister_chantiers import ListerChantiers
from app.shared.api.acteur import ActeurCourant

# Les erreurs possibles, documentées dans OpenAPI pour le client généré. Leur corps
# est celui de la traduction centrale (RFC 9457).
ERREURS: dict[int | str, dict[str, Any]] = {
    HTTPStatus.BAD_REQUEST: {"description": "Profil `X-Profil` absent ou inconnu."},
    HTTPStatus.FORBIDDEN: {"description": "Action réservée à un chef."},
    HTTPStatus.NOT_FOUND: {"description": "Chantier introuvable."},
    HTTPStatus.UNPROCESSABLE_ENTITY: {"description": "Données invalides."},
}


class FournisseursChantiers(Protocol):
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


def creer_routeur(fournisseurs: FournisseursChantiers) -> APIRouter:
    """Crée le routeur des chantiers, branché sur les cas d'usage fournis."""
    routeur = APIRouter(prefix="/chantiers", tags=["chantiers"], responses=ERREURS)

    @routeur.post("", status_code=HTTPStatus.CREATED, summary="Crée un chantier")
    def creer(
        requete: CreerChantierRequete,
        acteur: ActeurCourant,
        cas_usage: Annotated[CreerChantier, Depends(fournisseurs.creer_chantier)],
    ) -> ChantierReponse:
        return reponse_depuis(cas_usage.executer(commande_depuis(requete), acteur))

    @routeur.get("", summary="Liste les chantiers, avec leur avancement")
    def lister(
        acteur: ActeurCourant,
        cas_usage: Annotated[ListerChantiers, Depends(fournisseurs.lister_chantiers)],
    ) -> list[ChantierReponse]:
        return [reponse_depuis(vue) for vue in cas_usage.executer(acteur)]

    @routeur.get("/{chantier_id}", summary="Consulte un chantier")
    def consulter(
        chantier_id: UUID,
        acteur: ActeurCourant,
        cas_usage: Annotated[ConsulterChantier, Depends(fournisseurs.consulter_chantier)],
    ) -> ChantierReponse:
        return reponse_depuis(cas_usage.executer(chantier_id, acteur))

    return routeur
