"""Ce que les middlewares de protection lisent d'une requête : adresse, catégorie, périmètre."""

import ipaddress

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
# Taille du bloc que reçoit un abonné IPv6 : il sert de clé à la place de l'adresse.
BITS_PREFIXE_IPV6 = 64


def cle_du_client(scope: Scope) -> str:
    """Donne la clé de comptage du client : son adresse IPv4, ou le bloc /64 de son adresse IPv6.

    Un abonné IPv6 reçoit au moins un bloc /64 (2^64 adresses) : compter par adresse exacte
    laisserait un robot changer d'adresse à chaque requête, sans jamais être limité, et
    remplir la liste des blocages (ADR 0016). Une IPv4 encapsulée (`::ffff:a.b.c.d`) compte
    comme l'IPv4.
    Une adresse absente donne `ADRESSE_INCONNUE` ; une valeur illisible est gardée telle quelle.

    Derrière le proxy, uvicorn met dans la requête l'adresse réelle (en-têtes de transfert de
    confiance) : on ne lit jamais soi-même un en-tête `X-Forwarded-For`, que le client
    pourrait falsifier.
    """
    client = scope.get("client")
    if not client:
        return ADRESSE_INCONNUE
    try:
        adresse = ipaddress.ip_address(str(client[0]))
    except ValueError:
        return str(client[0])
    return _cle_de(adresse)


def _cle_de(adresse: ipaddress.IPv4Address | ipaddress.IPv6Address) -> str:
    if isinstance(adresse, ipaddress.IPv4Address):
        return str(adresse)
    if adresse.ipv4_mapped is not None:
        return str(adresse.ipv4_mapped)
    return str(ipaddress.ip_network(f"{adresse}/{BITS_PREFIXE_IPV6}", strict=False))


def est_surveillee(scope: Scope) -> bool:
    """Dit si la requête vise l'API, sonde de santé exceptée."""
    chemin: str = scope["path"]
    return chemin.startswith(PREFIXE_API) and chemin != CHEMIN_SONDE


def categorie_de(scope: Scope) -> CategorieAcces:
    """Classe la requête : toute méthode qui peut modifier des données est une écriture."""
    if scope["method"] in METHODES_EN_LECTURE:
        return CategorieAcces.LECTURE
    return CategorieAcces.ECRITURE
