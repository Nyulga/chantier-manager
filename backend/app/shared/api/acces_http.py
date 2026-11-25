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
# Taille du bloc qu'un abonné reçoit parfois (un /56 ou un /48, tunnels gratuits compris) :
# il sert de seconde clé, pour qu'un robot ne contourne pas la clé /64 en changeant de /64.
BITS_BLOC_IPV6_LARGE = 48

Adresse = ipaddress.IPv4Address | ipaddress.IPv6Address


def cle_du_client(scope: Scope) -> str:
    """Donne la clé de comptage du client : son adresse IPv4, ou le bloc /64 de son adresse IPv6.

    Un abonné IPv6 reçoit au moins un bloc /64 (2^64 adresses) : compter par adresse exacte
    laisserait un robot changer d'adresse à chaque requête, sans jamais être limité, et
    remplir la liste des blocages (ADR 0016). Une IPv4 encapsulée (`::ffff:a.b.c.d`) compte
    comme l'IPv4. Un abonné qui reçoit un bloc plus large qu'un /64 est repéré par la seconde
    clé de `cle_du_bloc_48`.
    Une adresse absente donne `ADRESSE_INCONNUE` ; une valeur illisible est gardée telle quelle.

    Derrière le proxy, uvicorn met dans la requête l'adresse réelle (en-têtes de transfert de
    confiance) : on ne lit jamais soi-même un en-tête `X-Forwarded-For`, que le client
    pourrait falsifier.
    """
    adresse = _adresse_du_client(scope)
    if adresse is None:
        return _texte_du_client(scope)
    if isinstance(adresse, ipaddress.IPv4Address):
        return str(adresse)
    if adresse.ipv4_mapped is not None:
        return str(adresse.ipv4_mapped)
    return str(_bloc(adresse, BITS_PREFIXE_IPV6))


def cle_du_bloc_48(scope: Scope) -> str | None:
    """Donne la seconde clé de comptage : le bloc /48 d'une adresse IPv6, sinon `None`.

    Une IPv4 (encapsulée ou non), une adresse absente ou illisible n'ont pas de seconde
    clé : leur clé habituelle suffit, il n'existe pas de bloc plus large à surveiller.
    """
    adresse = _adresse_du_client(scope)
    if not isinstance(adresse, ipaddress.IPv6Address) or adresse.ipv4_mapped is not None:
        return None
    return str(_bloc(adresse, BITS_BLOC_IPV6_LARGE))


def _texte_du_client(scope: Scope) -> str:
    client = scope.get("client")
    return str(client[0]) if client else ADRESSE_INCONNUE


def _adresse_du_client(scope: Scope) -> Adresse | None:
    """Lit l'adresse du client ; `None` si elle est absente ou illisible."""
    client = scope.get("client")
    if not client:
        return None
    try:
        return ipaddress.ip_address(str(client[0]))
    except ValueError:
        return None


def _bloc(adresse: ipaddress.IPv6Address, bits: int) -> ipaddress.IPv6Network:
    # Le réseau est construit depuis la valeur entière, jamais depuis le texte de l'adresse :
    # un texte avec zone (`fe80::1%eth0`) ne se reconvertit pas toujours en réseau, et une
    # exception ici ferait répondre 500 à toutes les requêtes. `IPv6Network` (et non
    # `ip_network`) évite qu'une petite valeur (`::1`) soit prise pour un réseau IPv4.
    return ipaddress.IPv6Network((int(adresse), bits), strict=False)


def est_surveillee(scope: Scope) -> bool:
    """Dit si la requête vise l'API, sonde de santé exceptée."""
    chemin: str = scope["path"]
    return chemin.startswith(PREFIXE_API) and chemin != CHEMIN_SONDE


def categorie_de(scope: Scope) -> CategorieAcces:
    """Classe la requête : toute méthode qui peut modifier des données est une écriture."""
    if scope["method"] in METHODES_EN_LECTURE:
        return CategorieAcces.LECTURE
    return CategorieAcces.ECRITURE
