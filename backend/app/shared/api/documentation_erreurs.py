"""Documentation OpenAPI des erreurs d'une route : leur statut, leur sens et leur corps."""

from http import HTTPStatus
from typing import Any

from app.shared.api.schemas import ProblemeReponse, ProblemeValidationReponse

DESCRIPTION_PAR_STATUT: dict[HTTPStatus, str] = {
    HTTPStatus.BAD_REQUEST: "Profil `X-Profil` absent ou inconnu.",
    HTTPStatus.FORBIDDEN: "Action non permise à ce profil.",
    HTTPStatus.NOT_FOUND: "Ressource introuvable, hors du périmètre ou identifiant mal formé.",
    HTTPStatus.CONFLICT: (
        "Action impossible dans l'état actuel, ressource modifiée entre-temps "
        "ou plafond de volume de la démo atteint."
    ),
    HTTPStatus.UNPROCESSABLE_ENTITY: "Données invalides : `erreurs` désigne les champs en cause.",
    HTTPStatus.SERVICE_UNAVAILABLE: "Service momentanément indisponible : réessayer plus tard.",
}


def erreurs_documentees(*statuts: HTTPStatus) -> dict[int | str, dict[str, Any]]:
    """Construit le paramètre `responses` d'un routeur pour les erreurs de ces statuts.

    Chaque erreur a le corps RFC 9457 de la traduction centrale (`ProblemeReponse`) ;
    le 422 y ajoute la liste des erreurs par champ. Le client TypeScript généré
    connaît ainsi la forme de toutes les erreurs.
    """
    return {
        statut.value: {
            "description": DESCRIPTION_PAR_STATUT[statut],
            "model": (
                ProblemeValidationReponse
                if statut is HTTPStatus.UNPROCESSABLE_ENTITY
                else ProblemeReponse
            ),
        }
        for statut in statuts
    }
