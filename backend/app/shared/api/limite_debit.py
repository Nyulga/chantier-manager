"""Limite de débit : refuse en 429 les adresses qui dépassent leur quota d'accès."""

from http import HTTPStatus

from starlette.types import ASGIApp, Receive, Scope, Send

from app.shared.api.acces_http import categorie_de, cle_du_client, est_surveillee
from app.shared.api.erreurs import MESSAGE_TROP_DE_DEMANDES, reponse_probleme
from app.shared.application.ports import LimiteurDebit


class MiddlewareLimiteDebit:
    """Compte chaque accès à l'API par adresse, et refuse ceux qui dépassent le seuil.

    Il est séparé du blocage des adresses piégées : l'un applique un quota, l'autre une
    sanction. Les seuils et la fenêtre appartiennent au limiteur (composition root).
    """

    def __init__(self, app: ASGIApp, limiteur: LimiteurDebit) -> None:
        self._app = app
        self._limiteur = limiteur

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """Laisse passer l'accès permis ; sinon répond 429 sans appeler la route."""
        if scope["type"] != "http" or not est_surveillee(scope):
            await self._app(scope, receive, send)
            return
        delai = self._limiteur.consommer(cle_du_client(scope), categorie_de(scope))
        if delai is None:
            await self._app(scope, receive, send)
            return
        # `Retry-After` recopie le délai du limiteur, déjà en secondes entières (RFC 9110).
        reponse = reponse_probleme(
            HTTPStatus.TOO_MANY_REQUESTS, MESSAGE_TROP_DE_DEMANDES, {"Retry-After": str(delai)}
        )
        await reponse(scope, receive, send)
