"""Fausses adresses pièges : un robot qui les demande est bloqué en écriture.

Aucun visiteur humain ne demande ces chemins : ce sont ceux que les robots essaient au
hasard, à la recherche d'un WordPress, d'un fichier de secrets ou d'un dépôt Git oublié.
Les toucher suffit à se désigner comme robot.
"""

from http import HTTPStatus

from fastapi import APIRouter, HTTPException, Request
from fastapi.routing import APIRoute
from starlette.routing import Match
from starlette.types import Scope

from app.shared.api.acces_http import cle_du_client
from app.shared.application.ports import ListeAdressesBloquees

# Chemins que seul un robot demande. Ils sont hors de `/api` : le proxy les envoie à l'API
# (`deploy/`), qui les traite comme des adresses inconnues, mais retient l'adresse qui les
# a demandés.
CHEMINS_PIEGES = (
    "/wp-admin",
    "/wp-login.php",
    "/.env",
    # Tout ce qui se trouve sous `/.git/` est un piège : un robot qui cherche un dépôt oublié
    # essaie `HEAD`, `objects/…`, `config`, etc.
    "/.git",
    "/phpmyadmin",
    "/xmlrpc.php",
)
# Les navigateurs actuels envoient cet en-tête sur toutes leurs requêtes, et un script de
# robot ne l'envoie pas. Il sert à ne bloquer que les robots (ADR 0016).
EN_TETE_NAVIGATEUR = "sec-fetch-site"
METHODES_PIEGES = ["GET", "HEAD", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]


def est_chemin_piege(chemin: str) -> bool:
    """Dit si le chemin est un piège ou se trouve sous un piège, sans tenir compte de la casse.

    Un robot essaie `/WP-ADMIN` aussi bien que `/wp-admin` : une variante en majuscules ne doit
    échapper ni au blocage ni à la limite de débit. Les chemins légitimes (`/api/...`) ne
    commencent par aucun piège, et `/wp-administrator` n'en est pas un.
    """
    minuscules = chemin.lower()
    return any(
        minuscules == piege or minuscules.startswith(f"{piege}/") for piege in CHEMINS_PIEGES
    )


class RoutePiege(APIRoute):
    """Route piège : elle reconnaît son chemin sans tenir compte de la casse.

    Les routes de FastAPI comparent les chemins en tenant compte de la casse. Plutôt que de
    réécrire l'adresse demandée dans un middleware (qui toucherait toutes les routes), seule
    la comparaison des pièges est assouplie, ici.
    """

    def matches(self, scope: Scope) -> tuple[Match, Scope]:
        """Compare le chemin demandé, mis en minuscules, au chemin de la route."""
        return super().matches({**scope, "path": scope["path"].lower()})


def creer_routeur_pieges(liste: ListeAdressesBloquees) -> APIRouter:
    """Crée le routeur des pièges : chaque chemin, et ses sous-chemins, bloque l'adresse.

    La réponse est celle d'une adresse inconnue (même statut, même corps), pour qu'un
    robot ne puisse pas distinguer un piège d'une page qui n'existe pas.

    L'adresse n'est bloquée que si la requête ne vient pas d'un navigateur : sinon une
    page d'un site tiers (`<img src="https://démo/wp-admin">`) ferait bloquer le visiteur
    qui la consulte, à son insu. Le robot, lui, n'envoie pas `Sec-Fetch-Site` (ADR 0016).
    """
    routeur = APIRouter(include_in_schema=False, route_class=RoutePiege)

    def piege(requete: Request) -> None:
        if EN_TETE_NAVIGATEUR not in requete.headers:
            liste.bloquer(cle_du_client(requete.scope))
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND)

    for chemin in CHEMINS_PIEGES:
        routeur.add_api_route(chemin, piege, methods=METHODES_PIEGES)
        routeur.add_api_route(f"{chemin}/{{sous_chemin:path}}", piege, methods=METHODES_PIEGES)
    return routeur
