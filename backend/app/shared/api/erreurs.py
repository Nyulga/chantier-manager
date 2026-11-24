"""Traduction centrale des erreurs en réponses HTTP au format RFC 9457.

C'est le seul endroit qui fait le lien entre les erreurs du domaine et les codes HTTP
(règle 04, Exception Translation). Les messages sont en français, et aucune trace
interne n'est jamais renvoyée.
"""

import logging
from collections.abc import Mapping
from http import HTTPStatus

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.shared.api.en_tetes_securite import EN_TETES_SECURITE
from app.shared.api.erreurs_validation import concerne_le_chemin, erreurs_par_champ
from app.shared.api.schemas import (
    ErreurChampReponse,
    ProblemeReponse,
    ProblemeValidationReponse,
)
from app.shared.application.erreurs import PlafondAtteintError, ServiceIndisponibleError
from app.shared.domain.acteur import Role
from app.shared.domain.erreurs import (
    AccesRefuseError,
    ConflitVersionError,
    NonTrouveError,
    TransitionInterditeError,
    ValeurInvalideError,
)

TYPE_PROBLEME = "application/problem+json"
TYPE_PAR_DEFAUT = "about:blank"
MESSAGE_ERREUR_INTERNE = "Une erreur interne est survenue."
MESSAGE_REQUETE_INVALIDE = "Les données envoyées sont invalides."
MESSAGE_RESSOURCE_INCONNUE = "Cette ressource n'existe pas."
MESSAGE_METHODE_NON_PERMISE = "Cette méthode n'est pas permise sur cette ressource."
MESSAGE_ERREUR_HTTP = "La requête n'a pas pu être traitée."
# Refus neutre : il ne dit pas pourquoi (adresse bloquée, champ piège rempli), pour ne pas
# apprendre à un robot ce qui l'a trahi. Le même texte sert au middleware et au champ piège.
MESSAGE_ACTION_REFUSEE = "Cette action n'est pas permise."
MESSAGE_TROP_DE_DEMANDES = "Trop de demandes. Réessaie dans quelques instants."
MESSAGE_CORPS_TROP_VOLUMINEUX = "Le corps de la requête est trop volumineux."
MESSAGE_SERVICE_INDISPONIBLE = (
    "Le service est momentanément indisponible : réessaie dans un instant."
)
# Les profils acceptés sont tirés de `Role` : ajouter un rôle met à jour le message
# et la documentation de l'en-tête, sans liste à recopier à la main.
PROFILS_ACCEPTES = " ou ".join(f"« {role.value} »" for role in Role)
MESSAGE_PROFIL_INVALIDE = f"L'en-tête X-Profil doit valoir {PROFILS_ACCEPTES}."

journal = logging.getLogger(__name__)


class ProfilInvalideError(Exception):
    """Le profil de l'en-tête `X-Profil` est absent ou inconnu.

    Ce n'est pas une erreur du domaine : elle vient de la façon dont le squelette
    désigne l'acteur, et disparaîtra avec l'authentification de la phase 2.
    """


# Les erreurs du domaine qui se traduisent par un simple statut. `ValeurInvalideError`
# a son propre traducteur : elle ajoute le champ en cause.
STATUT_PAR_ERREUR: dict[type[Exception], HTTPStatus] = {
    NonTrouveError: HTTPStatus.NOT_FOUND,
    AccesRefuseError: HTTPStatus.FORBIDDEN,
    TransitionInterditeError: HTTPStatus.CONFLICT,
    ConflitVersionError: HTTPStatus.CONFLICT,
    # Un plafond de volume atteint ne se résout pas en réessayant : c'est un conflit avec
    # l'état de la démo, qui ne change que si le propriétaire en décide.
    PlafondAtteintError: HTTPStatus.CONFLICT,
}

TITRE_PAR_STATUT: dict[int, str] = {
    HTTPStatus.BAD_REQUEST: "Requête incorrecte",
    HTTPStatus.FORBIDDEN: "Accès refusé",
    HTTPStatus.NOT_FOUND: "Ressource introuvable",
    HTTPStatus.METHOD_NOT_ALLOWED: "Méthode non autorisée",
    HTTPStatus.CONFLICT: "Conflit",
    HTTPStatus.CONTENT_TOO_LARGE: "Requête trop volumineuse",
    HTTPStatus.UNPROCESSABLE_ENTITY: "Données invalides",
    HTTPStatus.TOO_MANY_REQUESTS: "Trop de demandes",
    HTTPStatus.INTERNAL_SERVER_ERROR: "Erreur interne",
    HTTPStatus.SERVICE_UNAVAILABLE: "Service indisponible",
}
TITRE_PAR_DEFAUT = "Erreur"

# Message des erreurs de routage de Starlette, dont le texte natif est en anglais.
DETAIL_HTTP_PAR_STATUT: dict[int, str] = {
    HTTPStatus.FORBIDDEN: MESSAGE_ACTION_REFUSEE,
    HTTPStatus.NOT_FOUND: MESSAGE_RESSOURCE_INCONNUE,
    HTTPStatus.METHOD_NOT_ALLOWED: MESSAGE_METHODE_NON_PERMISE,
}


def _reponse(probleme: ProblemeReponse, en_tetes: Mapping[str, str] | None = None) -> JSONResponse:
    return JSONResponse(
        probleme.model_dump(mode="json"),
        status_code=probleme.status,
        media_type=TYPE_PROBLEME,
        headers=en_tetes,
    )


def reponse_probleme(
    statut: int, detail: str, en_tetes: Mapping[str, str] | None = None
) -> JSONResponse:
    """Construit une réponse `application/problem+json` (RFC 9457)."""
    probleme = ProblemeReponse(
        type=TYPE_PAR_DEFAUT,
        title=TITRE_PAR_STATUT.get(statut, TITRE_PAR_DEFAUT),
        status=statut,
        detail=detail,
    )
    return _reponse(probleme, en_tetes)


def reponse_validation(detail: str, erreurs: list[ErreurChampReponse]) -> JSONResponse:
    """Construit la réponse 422, avec la liste des erreurs par champ."""
    probleme = ProblemeValidationReponse(
        type=TYPE_PAR_DEFAUT,
        title=TITRE_PAR_STATUT[HTTPStatus.UNPROCESSABLE_ENTITY],
        status=HTTPStatus.UNPROCESSABLE_ENTITY,
        detail=detail,
        erreurs=erreurs,
    )
    return _reponse(probleme)


async def _traduire_erreur_metier(_requete: Request, erreur: Exception) -> JSONResponse:
    # Les messages des erreurs du domaine sont écrits pour être affichés (règle 01).
    statut = next(
        statut for classe, statut in STATUT_PAR_ERREUR.items() if isinstance(erreur, classe)
    )
    return reponse_probleme(statut, str(erreur))


async def _traduire_valeur_invalide(_requete: Request, erreur: ValeurInvalideError) -> JSONResponse:
    erreurs = [ErreurChampReponse(champ=erreur.champ, message=str(erreur))] if erreur.champ else []
    return reponse_validation(str(erreur), erreurs)


async def _traduire_profil(_requete: Request, _erreur: Exception) -> JSONResponse:
    return reponse_probleme(HTTPStatus.BAD_REQUEST, MESSAGE_PROFIL_INVALIDE)


async def _traduire_requete_invalide(
    _requete: Request, erreur: RequestValidationError
) -> JSONResponse:
    # Un identifiant mal formé dans le chemin désigne une ressource qui n'existe pas, comme
    # n'importe quel identifiant inconnu : un 422 le distinguerait, sans rien apprendre de plus.
    if concerne_le_chemin(erreur):
        return reponse_probleme(HTTPStatus.NOT_FOUND, MESSAGE_RESSOURCE_INCONNUE)
    # Le détail natif de FastAPI renvoie la valeur envoyée : on ne le recopie pas.
    return reponse_validation(MESSAGE_REQUETE_INVALIDE, erreurs_par_champ(erreur))


async def _traduire_erreur_http(_requete: Request, erreur: StarletteHTTPException) -> JSONResponse:
    # Le texte natif est en anglais ; l'en-tête `Allow` d'un 405 est conservé, car le
    # protocole HTTP l'exige.
    detail = DETAIL_HTTP_PAR_STATUT.get(erreur.status_code, MESSAGE_ERREUR_HTTP)
    return reponse_probleme(erreur.status_code, detail, erreur.headers)


async def _traduire_service_indisponible(
    _requete: Request, erreur: ServiceIndisponibleError
) -> JSONResponse:
    # La cause complète est consignée, pour diagnostiquer la panne : son message est journalisé
    # tel quel. Le moteur SQL masque les paramètres des requêtes (`hide_parameters`), et la
    # réponse reste générique : elle ne recopie jamais la cause.
    journal.error("Service indisponible.", exc_info=erreur)
    return reponse_probleme(HTTPStatus.SERVICE_UNAVAILABLE, MESSAGE_SERVICE_INDISPONIBLE)


async def _traduire_erreur_inconnue(_requete: Request, _erreur: Exception) -> JSONResponse:
    # Aucun détail : une trace interne aiderait un attaquant. Le serveur consigne l'erreur.
    # Starlette produit cette réponse hors de la pile des middlewares : les en-têtes de
    # sécurité sont donc posés ici, sinon la 500 en serait privée.
    return reponse_probleme(
        HTTPStatus.INTERNAL_SERVER_ERROR, MESSAGE_ERREUR_INTERNE, EN_TETES_SECURITE
    )


def enregistrer_gestionnaires_erreurs(application: FastAPI) -> None:
    """Branche la traduction des erreurs sur l'application."""
    for classe in STATUT_PAR_ERREUR:
        application.add_exception_handler(classe, _traduire_erreur_metier)
    # Les traducteurs qui lisent l'erreur passent par le décorateur, qui accepte un type
    # d'erreur précis ; `add_exception_handler` n'accepte que des traducteurs d'`Exception`.
    application.exception_handler(ValeurInvalideError)(_traduire_valeur_invalide)
    application.exception_handler(RequestValidationError)(_traduire_requete_invalide)
    application.exception_handler(StarletteHTTPException)(_traduire_erreur_http)
    application.exception_handler(ServiceIndisponibleError)(_traduire_service_indisponible)
    application.add_exception_handler(ProfilInvalideError, _traduire_profil)
    application.add_exception_handler(Exception, _traduire_erreur_inconnue)
