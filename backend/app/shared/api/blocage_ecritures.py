"""Blocage des écritures : une adresse piégée n'écrit plus, mais peut encore lire."""

from http import HTTPStatus

from starlette.types import ASGIApp, Receive, Scope, Send

from app.shared.api.acces_http import categorie_de, cle_du_client, est_surveillee
from app.shared.api.erreurs import MESSAGE_ACTION_REFUSEE, reponse_probleme
from app.shared.application.ports import CategorieAcces, ListeAdressesBloquees


class MiddlewareBlocageEcritures:
    """Refuse en 403 les écritures d'une adresse bloquée, sans délai ni explication.

    Le refus est immédiat et neutre : il ne dit pas que l'adresse est piégée, et ne fait pas
    attendre le robot, qui n'apprend ainsi rien. Les lectures restent permises, pour qu'une
    personne qui partage l'adresse du robot puisse encore consulter la démo. Il est séparé de
    la limite de débit : une sanction et un quota sont deux règles distinctes, et un refus
    par blocage ne doit pas consommer le quota.
    """

    def __init__(self, app: ASGIApp, liste: ListeAdressesBloquees) -> None:
        self._app = app
        self._liste = liste

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """Répond 403 à l'écriture d'une adresse bloquée ; laisse passer tout le reste."""
        if scope["type"] == "http" and self._est_ecriture_bloquee(scope):
            reponse = reponse_probleme(HTTPStatus.FORBIDDEN, MESSAGE_ACTION_REFUSEE)
            await reponse(scope, receive, send)
            return
        await self._app(scope, receive, send)

    def _est_ecriture_bloquee(self, scope: Scope) -> bool:
        return (
            est_surveillee(scope)
            and categorie_de(scope) is CategorieAcces.ECRITURE
            and self._liste.est_bloquee(cle_du_client(scope))
        )
