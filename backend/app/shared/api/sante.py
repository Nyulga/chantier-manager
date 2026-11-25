"""Route de santé : permet à Docker, au proxy et à la CI de savoir si l'API répond."""

from http import HTTPStatus

from fastapi import APIRouter, Response

from app.shared.api.documentation_erreurs import erreurs_documentees
from app.shared.api.schemas import ReponseSante

routeur = APIRouter(tags=["santé"])


# Le middleware des noms d'hôte acceptés s'applique aussi à la sonde : il peut répondre 400.
@routeur.get(
    "/health",
    response_model=ReponseSante,
    status_code=HTTPStatus.OK,
    responses=erreurs_documentees(HTTPStatus.BAD_REQUEST),
)
def lire_sante() -> ReponseSante:
    """Renvoie `{"statut": "ok"}` : elle ne touche ni la base ni aucun service externe.

    Une sonde de vie ne doit dépendre de rien, sinon une panne de la base ferait
    redémarrer l'API pour rien.
    """
    return ReponseSante(statut="ok")


@routeur.head("/health", status_code=HTTPStatus.OK, include_in_schema=False)
def lire_sante_sans_corps() -> Response:
    """Répond 200 sans corps : certaines sondes (proxy, supervision) testent en `HEAD`."""
    return Response(status_code=HTTPStatus.OK)
