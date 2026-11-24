"""Ce que les middlewares de protection lisent d'une requête : adresse, catégorie, périmètre."""

from starlette.types import Scope

from app.shared.application.ports import CategorieAcces

PREFIXE_API = "/api/"
# La sonde de santé du conteneur (et du proxy) ne doit jamais être refusée : une limite ou
# un blocage la ferait échouer, et l'orchestrateur redémarrerait l'API pour rien.
CHEMIN_SONDE = "/api/health"
METHODES_EN_LECTURE = frozenset({"GET", "HEAD", "OPTIONS"})
# Adresse utilisée quand le serveur ne donne pas celle du client : tous ces accès partagent
# alors un même compte, ce qui est plus sûr que de ne rien compter.
ADRESSE_INCONNUE = "inconnue"


def adresse_du_client(scope: Scope) -> str:
    """Donne l'adresse du client, telle que le serveur l'a fixée dans la requête.

    Derrière le proxy, uvicorn y met l'adresse réelle (en-têtes de transfert de confiance) :
    on ne lit jamais soi-même un en-tête `X-Forwarded-For`, que le client pourrait falsifier.
    """
    client = scope.get("client")
    return str(client[0]) if client else ADRESSE_INCONNUE


def est_surveillee(scope: Scope) -> bool:
    """Dit si la requête vise l'API, sonde de santé exceptée."""
    chemin: str = scope["path"]
    return chemin.startswith(PREFIXE_API) and chemin != CHEMIN_SONDE


def categorie_de(scope: Scope) -> CategorieAcces:
    """Classe la requête : toute méthode qui peut modifier des données est une écriture."""
    if scope["method"] in METHODES_EN_LECTURE:
        return CategorieAcces.LECTURE
    return CategorieAcces.ECRITURE
