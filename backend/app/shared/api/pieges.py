"""Fausses adresses pièges : un robot qui les demande est bloqué en écriture.

Aucun visiteur humain ne demande ces chemins : ce sont ceux que les robots essaient au
hasard, à la recherche d'un WordPress, d'un fichier de secrets ou d'un dépôt Git oublié.
Les toucher suffit à se désigner comme robot.
"""

from http import HTTPStatus

from fastapi import APIRouter, HTTPException, Request

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


def creer_routeur_pieges(liste: ListeAdressesBloquees) -> APIRouter:
    """Crée le routeur des pièges : chaque chemin, et ses sous-chemins, bloque l'adresse.

    La réponse est celle d'une adresse inconnue (même statut, même corps), pour qu'un
    robot ne puisse pas distinguer un piège d'une page qui n'existe pas.

    L'adresse n'est bloquée que si la requête ne vient pas d'un navigateur : sinon une
    page d'un site tiers (`<img src="https://démo/wp-admin">`) ferait bloquer le visiteur
    qui la consulte, à son insu. Le robot, lui, n'envoie pas `Sec-Fetch-Site` (ADR 0016).
    """
    routeur = APIRouter(include_in_schema=False)

    def piege(requete: Request) -> None:
        if EN_TETE_NAVIGATEUR not in requete.headers:
            liste.bloquer(cle_du_client(requete.scope))
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND)

    for chemin in CHEMINS_PIEGES:
        routeur.add_api_route(chemin, piege, methods=METHODES_PIEGES)
        routeur.add_api_route(f"{chemin}/{{sous_chemin:path}}", piege, methods=METHODES_PIEGES)
    return routeur
