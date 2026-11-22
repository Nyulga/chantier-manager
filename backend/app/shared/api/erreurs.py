"""Traduction centrale des erreurs en réponses HTTP au format RFC 9457.

C'est le seul endroit qui fait le lien entre les erreurs du domaine et les codes HTTP
(règle 04, Exception Translation). Les messages sont en français, et aucune trace
interne n'est jamais renvoyée.
"""

from http import HTTPStatus

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.shared.domain.erreurs import (
    AccesRefuseError,
    ConflitVersionError,
    NonTrouveError,
    TransitionInterditeError,
    ValeurInvalideError,
)

TYPE_PROBLEME = "application/problem+json"
MESSAGE_ERREUR_INTERNE = "Une erreur interne est survenue."
MESSAGE_REQUETE_INVALIDE = "Les données envoyées sont invalides."
MESSAGE_PROFIL_INVALIDE = "L'en-tête X-Profil doit valoir « chef » ou « ouvrier »."


class ProfilInvalideError(Exception):
    """Le profil de l'en-tête `X-Profil` est absent ou inconnu.

    Ce n'est pas une erreur du domaine : elle vient de la façon dont le squelette
    désigne l'acteur, et disparaîtra avec l'authentification de la phase 2.
    """


STATUT_PAR_ERREUR: dict[type[Exception], HTTPStatus] = {
    NonTrouveError: HTTPStatus.NOT_FOUND,
    AccesRefuseError: HTTPStatus.FORBIDDEN,
    TransitionInterditeError: HTTPStatus.CONFLICT,
    ConflitVersionError: HTTPStatus.CONFLICT,
    ValeurInvalideError: HTTPStatus.UNPROCESSABLE_ENTITY,
}

TITRE_PAR_STATUT = {
    HTTPStatus.BAD_REQUEST: "Requête incorrecte",
    HTTPStatus.FORBIDDEN: "Accès refusé",
    HTTPStatus.NOT_FOUND: "Ressource introuvable",
    HTTPStatus.CONFLICT: "Conflit",
    HTTPStatus.UNPROCESSABLE_ENTITY: "Données invalides",
    HTTPStatus.INTERNAL_SERVER_ERROR: "Erreur interne",
}


def reponse_probleme(statut: HTTPStatus, detail: str) -> JSONResponse:
    """Construit une réponse `application/problem+json` (RFC 9457)."""
    corps = {
        "type": "about:blank",
        "title": TITRE_PAR_STATUT[statut],
        "status": statut.value,
        "detail": detail,
    }
    return JSONResponse(corps, status_code=statut.value, media_type=TYPE_PROBLEME)


async def _traduire_erreur_metier(_requete: Request, erreur: Exception) -> JSONResponse:
    # Les messages des erreurs du domaine sont écrits pour être affichés (règle 01).
    statut = next(
        statut for classe, statut in STATUT_PAR_ERREUR.items() if isinstance(erreur, classe)
    )
    return reponse_probleme(statut, str(erreur))


async def _traduire_profil(_requete: Request, _erreur: Exception) -> JSONResponse:
    return reponse_probleme(HTTPStatus.BAD_REQUEST, MESSAGE_PROFIL_INVALIDE)


async def _traduire_requete_invalide(_requete: Request, _erreur: Exception) -> JSONResponse:
    # Le détail natif de FastAPI renvoie la valeur envoyée : on ne le recopie pas.
    return reponse_probleme(HTTPStatus.UNPROCESSABLE_ENTITY, MESSAGE_REQUETE_INVALIDE)


async def _traduire_erreur_inconnue(_requete: Request, _erreur: Exception) -> JSONResponse:
    # Aucun détail : une trace interne aiderait un attaquant. Le serveur consigne l'erreur.
    return reponse_probleme(HTTPStatus.INTERNAL_SERVER_ERROR, MESSAGE_ERREUR_INTERNE)


def enregistrer_gestionnaires_erreurs(application: FastAPI) -> None:
    """Branche la traduction des erreurs sur l'application."""
    for classe in STATUT_PAR_ERREUR:
        application.add_exception_handler(classe, _traduire_erreur_metier)
    application.add_exception_handler(ProfilInvalideError, _traduire_profil)
    application.add_exception_handler(RequestValidationError, _traduire_requete_invalide)
    application.add_exception_handler(Exception, _traduire_erreur_inconnue)
