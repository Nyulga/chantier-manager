"""Documentation OpenAPI des erreurs d'une route : leur statut, leur sens et leur corps."""

from http import HTTPStatus
from typing import Any

from app.shared.api.schemas import ProblemeReponse, ProblemeValidationReponse

DESCRIPTION_PAR_STATUT: dict[HTTPStatus, str] = {
    HTTPStatus.BAD_REQUEST: "Profil `X-Profil` absent ou inconnu, ou nom d'hôte refusé.",
    HTTPStatus.FORBIDDEN: (
        "Action non permise à ce profil, ou écriture refusée par les protections (adresse bloquée)."
    ),
    HTTPStatus.NOT_FOUND: "Ressource introuvable, hors du périmètre ou identifiant mal formé.",
    HTTPStatus.CONFLICT: (
        "Action impossible dans l'état actuel, ressource modifiée entre-temps "
        "ou plafond de volume de la démo atteint."
    ),
    HTTPStatus.CONTENT_TOO_LARGE: "Corps de la requête trop volumineux.",
    HTTPStatus.TOO_MANY_REQUESTS: (
        "Trop de requêtes depuis cette adresse : réessayer après le délai de `Retry-After`."
    ),
    HTTPStatus.UNPROCESSABLE_ENTITY: "Données invalides : `erreurs` désigne les champs en cause.",
    HTTPStatus.SERVICE_UNAVAILABLE: "Service momentanément indisponible : réessayer plus tard.",
}

# Seul le 429 porte un en-tête : le délai d'attente avant de réessayer (RFC 9110).
EN_TETES_PAR_STATUT: dict[HTTPStatus, dict[str, Any]] = {
    HTTPStatus.TOO_MANY_REQUESTS: {
        "Retry-After": {
            "description": "Nombre de secondes à attendre avant de réessayer.",
            "schema": {"type": "string"},
        }
    }
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
            **({"headers": EN_TETES_PAR_STATUT[statut]} if statut in EN_TETES_PAR_STATUT else {}),
        }
        for statut in statuts
    }


# À déclarer sur les seules routes qui reçoivent un corps : un 413 n'y est pas possible ailleurs.
CORPS_TROP_VOLUMINEUX = erreurs_documentees(HTTPStatus.CONTENT_TOO_LARGE)
