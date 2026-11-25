"""Hôtes acceptés : refuse les requêtes dont l'en-tête `Host` n'est pas celui du site."""

from collections.abc import Sequence
from http import HTTPStatus

from starlette.types import ASGIApp, Receive, Scope, Send

from app.shared.api.erreurs import reponse_probleme

MESSAGE_HOTE_INCONNU = "Hôte non reconnu."


def _nom_d_hote(en_tete: str) -> str:
    """Retire le port d'un en-tête `Host`, y compris pour une adresse IPv6 entre crochets."""
    if en_tete.startswith("["):
        return en_tete[1 : en_tete.find("]")]
    return en_tete.partition(":")[0]


class MiddlewareHotesAcceptes:
    """Refuse en 400 toute requête dont l'hôte est absent ou hors de la liste.

    Un hôte inattendu signale un accès qui ne passe pas par le site (adresse IP directe,
    nom détourné). On le refuse en RFC 9457 plutôt qu'avec le texte brut de Starlette.
    La comparaison ignore le port et la casse. Le refus ne recopie pas l'hôte reçu. Les
    événements de démarrage (`lifespan`) ne portent pas d'en-tête : ils passent.
    """

    def __init__(self, app: ASGIApp, hotes: Sequence[str]) -> None:
        self._app = app
        self._hotes = frozenset(hote.lower() for hote in hotes)

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """Transmet la requête si son hôte est connu, sinon répond 400."""
        if scope["type"] == "lifespan" or self._hote_connu(scope):
            await self._app(scope, receive, send)
            return
        reponse = reponse_probleme(HTTPStatus.BAD_REQUEST, MESSAGE_HOTE_INCONNU)
        await reponse(scope, receive, send)

    def _hote_connu(self, scope: Scope) -> bool:
        for nom, valeur in scope["headers"]:
            if nom == b"host":
                return _nom_d_hote(valeur.decode("latin-1").lower()) in self._hotes
        return False
