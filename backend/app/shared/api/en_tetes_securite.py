"""En-têtes de sécurité, posés sur toutes les réponses de l'API, erreurs comprises."""

from collections.abc import Mapping

from starlette.datastructures import MutableHeaders
from starlette.types import ASGIApp, Message, Receive, Scope, Send

# Source de vérité des en-têtes pour l'application. Ils doivent rester identiques à ceux du
# bloc `header` de `deploy/Caddyfile.extrait` (`test_en_tetes_securite.py` le vérifie) : le
# proxy les pose sur le site, l'application les pose en plus sur l'API, pour ne pas dépendre
# de lui (défense en profondeur).
EN_TETES_SECURITE: Mapping[str, str] = {
    "Strict-Transport-Security": "max-age=31536000",
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Content-Security-Policy": (
        "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; "
        "font-src 'self'; connect-src 'self'; object-src 'none'; base-uri 'self'; "
        "form-action 'self'; frame-ancestors 'none'"
    ),
    "Permissions-Policy": "camera=(), microphone=(), geolocation=(), payment=(), usb=()",
    "Cross-Origin-Opener-Policy": "same-origin",
}


class MiddlewareEnTetesSecurite:
    """Ajoute les en-têtes de sécurité à chaque réponse HTTP.

    C'est un middleware ASGI pur : il ne lit ni ne retient le corps. Empilé au plus à
    l'extérieur, il enveloppe aussi les refus produits par les autres middlewares.
    """

    def __init__(self, app: ASGIApp) -> None:
        self._app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """Transmet la requête, en complétant l'en-tête de la réponse au passage."""
        if scope["type"] != "http":
            await self._app(scope, receive, send)
            return

        async def envoyer(message: Message) -> None:
            if message["type"] == "http.response.start":
                en_tetes = MutableHeaders(scope=message)
                for nom, valeur in EN_TETES_SECURITE.items():
                    en_tetes[nom] = valeur
            await send(message)

        await self._app(scope, receive, envoyer)
