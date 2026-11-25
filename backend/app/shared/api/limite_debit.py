"""Limite de débit : refuse en 429 les adresses qui dépassent leur quota d'accès."""

from http import HTTPStatus

from starlette.types import ASGIApp, Receive, Scope, Send

from app.shared.api.acces_http import (
    categorie_de,
    cle_du_bloc_48,
    cle_du_client,
    est_surveillee,
)
from app.shared.api.erreurs import MESSAGE_TROP_DE_DEMANDES, reponse_probleme
from app.shared.api.pieges import est_chemin_piege
from app.shared.application.ports import LimiteurDebit


class MiddlewareLimiteDebit:
    """Compte chaque accès à l'API et aux pièges par adresse, et refuse ceux qui dépassent le seuil.

    Il est séparé du blocage des adresses piégées : l'un applique un quota, l'autre une
    sanction. Les pièges sont comptés ici mais ne sont pas bloqués par l'autre middleware :
    un piège répond toujours le même 404 qu'une adresse inconnue, et un robot qui les
    martèle est freiné par le quota.

    Deux limiteurs, aux seuils différents (la composition root les fournit) : le premier
    compte la clé habituelle (IPv4 ou bloc /64), le second le bloc /48 d'une adresse IPv6.
    Le second seuil est plus haut, car plusieurs abonnés peuvent partager un /48 (issue #63).
    Les deux sont obligatoires : une protection facultative est une protection qu'on oublie.
    """

    def __init__(
        self, app: ASGIApp, limiteur: LimiteurDebit, limiteur_bloc_48: LimiteurDebit
    ) -> None:
        self._app = app
        self._limiteur = limiteur
        self._limiteur_bloc_48 = limiteur_bloc_48

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """Laisse passer l'accès permis ; sinon répond 429 sans appeler la route."""
        if scope["type"] != "http" or not _est_comptee(scope):
            await self._app(scope, receive, send)
            return
        delai = self._delai_de_refus(scope)
        if delai is None:
            await self._app(scope, receive, send)
            return
        # `Retry-After` recopie le délai du limiteur, déjà en secondes entières (RFC 9110).
        reponse = reponse_probleme(
            HTTPStatus.TOO_MANY_REQUESTS, MESSAGE_TROP_DE_DEMANDES, {"Retry-After": str(delai)}
        )
        await reponse(scope, receive, send)

    def _delai_de_refus(self, scope: Scope) -> int | None:
        """Donne le délai d'attente si l'accès est refusé, `None` s'il est permis.

        L'ordre est voulu : la clé habituelle d'abord, et le bloc /48 seulement si elle
        accepte. Une adresse qui insiste au-delà de son quota est refusée ici sans consommer
        celui du /48 : ses voisins du même bloc ne paient pas pour elle.
        """
        categorie = categorie_de(scope)
        delai = self._limiteur.consommer(cle_du_client(scope), categorie)
        cle_bloc = cle_du_bloc_48(scope)
        if delai is not None or cle_bloc is None:
            return delai
        return self._limiteur_bloc_48.consommer(cle_bloc, categorie)


def _est_comptee(scope: Scope) -> bool:
    # Le débit couvre l'API (sonde exceptée) et les pièges ; le blocage des écritures, lui,
    # ne couvre que l'API (`est_surveillee`) : un piège ne doit pas répondre 403 à une adresse
    # bloquée, ce qui le distinguerait d'une adresse inconnue.
    return est_surveillee(scope) or est_chemin_piege(scope["path"])
