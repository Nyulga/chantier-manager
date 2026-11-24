"""Limite de taille des corps de requête : refus en 413, y compris pour un corps découpé."""

from http import HTTPStatus

from starlette.types import ASGIApp, Message, Receive, Scope, Send

from app.shared.api.erreurs import MESSAGE_CORPS_TROP_VOLUMINEUX, reponse_probleme


class _CorpsBorne:
    """Compte les octets reçus d'un corps, et le coupe quand la limite est franchie."""

    def __init__(self, receive: Receive, send: Send, taille_max: int) -> None:
        self._receive = receive
        self._send = send
        self._taille_max = taille_max
        self._recus = 0
        self.depasse = False

    async def recevoir(self) -> Message:
        """Lit un morceau du corps ; au-delà de la limite, annonce la fin de la connexion."""
        if self.depasse:
            return {"type": "http.disconnect"}
        message = await self._receive()
        self._recus += len(message.get("body", b""))
        if self._recus > self._taille_max:
            self.depasse = True
            return {"type": "http.disconnect"}
        return message

    async def envoyer(self, message: Message) -> None:
        """Transmet la réponse de l'application, sauf si elle doit être remplacée par le 413."""
        if not self.depasse:
            await self._send(message)


class MiddlewareTailleCorps:
    """Refuse en 413 tout corps de plus de `taille_max` octets, avant que la route ne le lise.

    Deux cas, car l'en-tête `Content-Length` peut manquer ou mentir :
    - le corps annonce déjà une taille trop grande : refus immédiat, sans rien lire ;
    - le corps est envoyé par morceaux (sans `Content-Length`) : on compte les octets reçus
      et, dès que la limite est franchie, on coupe la lecture. L'application croit alors
      que le client a fermé la connexion, et on remplace sa réponse par le 413 : la
      réponse ne dépend pas de la façon dont l'application réagit à cette coupure.

    Le même plafond existe dans Caddy ; il est refait ici pour ne pas dépendre du proxy.
    """

    def __init__(self, app: ASGIApp, taille_max: int) -> None:
        self._app = app
        self._taille_max = taille_max

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """Transmet la requête si son corps reste sous la limite, sinon répond 413."""
        if scope["type"] != "http":
            await self._app(scope, receive, send)
            return
        if self._annonce_trop_gros(scope):
            await self._refuser(scope, receive, send)
            return
        await self._transmettre_en_comptant(scope, receive, send)

    def _annonce_trop_gros(self, scope: Scope) -> bool:
        for nom, valeur in scope["headers"]:
            # Une valeur illisible n'est pas annoncée comme trop grosse : le comptage des
            # octets réellement reçus reste la vraie protection.
            if nom == b"content-length" and valeur.isdigit():
                return int(valeur) > self._taille_max
        return False

    async def _transmettre_en_comptant(self, scope: Scope, receive: Receive, send: Send) -> None:
        corps = _CorpsBorne(receive, send, self._taille_max)
        try:
            await self._app(scope, corps.recevoir, corps.envoyer)
        except Exception:
            # Une erreur causée par la coupure n'a pas à remonter : la réponse est le 413.
            if not corps.depasse:
                raise
        if corps.depasse:
            await self._refuser(scope, receive, send)

    async def _refuser(self, scope: Scope, receive: Receive, send: Send) -> None:
        reponse = reponse_probleme(HTTPStatus.CONTENT_TOO_LARGE, MESSAGE_CORPS_TROP_VOLUMINEUX)
        await reponse(scope, receive, send)
