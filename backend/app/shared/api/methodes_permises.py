"""Méthodes permises sur un chemin : le contenu de l'en-tête `Allow` d'un 405."""

from starlette.requests import Request
from starlette.routing import Match

METHODES_SONDEES = ("GET", "HEAD", "POST", "PUT", "PATCH", "DELETE", "OPTIONS")


def methodes_permises(requete: Request) -> str:
    """Liste les méthodes qu'une route du chemin accepte, en les essayant une à une.

    Starlette ne regarde que la première route dont le chemin correspond : sur
    `/api/chantiers`, où `GET` et `POST` sont deux routes, `Allow` n'annonçait que l'une
    des deux (issue #69). Le protocole HTTP exige pourtant la liste complète. On sonde donc
    chaque méthode avec l'API publique de routage (`matches`), plutôt que de lire la structure
    interne des routeurs de FastAPI, qui change d'une version à l'autre.
    """
    routes = requete.app.router.routes
    permises = [
        methode
        for methode in METHODES_SONDEES
        if any(
            route.matches({**requete.scope, "method": methode})[0] is Match.FULL for route in routes
        )
    ]
    return ", ".join(permises)
