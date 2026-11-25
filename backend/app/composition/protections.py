"""Assemblage des protections de la démo publique : limite de débit, pièges et middlewares.

Les limiteurs et la liste d'adresses bloquées sont créés une seule fois par application :
les middlewares et les routes pièges doivent partager les mêmes instances, sinon une adresse
piégée par une route ne serait pas bloquée par le middleware. Il y a deux limiteurs : l'un
compte par adresse (IPv4 ou bloc IPv6 /64), l'autre par bloc IPv6 /48, à des seuils
multipliés par `FACTEUR_BLOC_IPV6_48` (issue #63). Ce fichier ne fait qu'assembler
(règle 06) ; les règles sont dans `shared`.
"""

from dataclasses import dataclass

from fastapi import FastAPI

from app.composition.parametres import Parametres
from app.shared.api.blocage_ecritures import MiddlewareBlocageEcritures
from app.shared.api.en_tetes_securite import MiddlewareEnTetesSecurite
from app.shared.api.hotes_acceptes import MiddlewareHotesAcceptes
from app.shared.api.limite_debit import MiddlewareLimiteDebit
from app.shared.api.taille_corps import MiddlewareTailleCorps
from app.shared.application.limites_debit import (
    DUREE_BLOCAGE_PIEGE,
    FACTEUR_BLOC_IPV6_48,
    FENETRE_DEBIT,
)
from app.shared.application.ports import CategorieAcces, LimiteurDebit, ListeAdressesBloquees
from app.shared.infrastructure.adresses_bloquees_memoire import MemoireListeAdressesBloquees
from app.shared.infrastructure.horloge_systeme import HorlogeSysteme
from app.shared.infrastructure.limiteur_debit_memoire import MemoireLimiteurDebit


@dataclass(frozen=True)
class Protections:
    """Les états partagés des protections : les deux limiteurs et la liste des adresses bloquées.

    `limiteur` compte par adresse ; `limiteur_bloc_48` compte par bloc IPv6 /48, à un seuil
    plus haut, pour qu'un robot ne contourne pas le premier en changeant de /64.
    """

    limiteur: LimiteurDebit
    limiteur_bloc_48: LimiteurDebit
    adresses_bloquees: ListeAdressesBloquees


def creer_protections(parametres: Parametres) -> Protections:
    """Crée les deux limiteurs et la liste d'adresses bloquées, en mémoire (ADR 0016).

    Le seuil du bloc /48 est le seuil réellement en vigueur, réglable par les paramètres,
    multiplié par `FACTEUR_BLOC_IPV6_48` : les deux restent ainsi dans le même rapport.
    """
    horloge = HorlogeSysteme()
    seuils = {
        CategorieAcces.ECRITURE: parametres.ecritures_par_minute,
        CategorieAcces.LECTURE: parametres.lectures_par_minute,
    }
    seuils_bloc_48 = {
        categorie: seuil * FACTEUR_BLOC_IPV6_48 for categorie, seuil in seuils.items()
    }
    return Protections(
        limiteur=MemoireLimiteurDebit(horloge, seuils, FENETRE_DEBIT),
        limiteur_bloc_48=MemoireLimiteurDebit(horloge, seuils_bloc_48, FENETRE_DEBIT),
        adresses_bloquees=MemoireListeAdressesBloquees(horloge, DUREE_BLOCAGE_PIEGE),
    )


def empiler_middlewares(
    application: FastAPI, protections: Protections, parametres: Parametres
) -> None:
    """Ajoute les middlewares de protection, du plus intérieur au plus extérieur.

    Starlette place le dernier ajouté au plus à l'extérieur. De l'extérieur vers l'intérieur :
    en-têtes de sécurité (ils couvrent aussi les refus des autres), hôtes, taille du corps,
    blocage des écritures, puis limite de débit. Le blocage passe avant le débit : un refus
    par blocage ne doit pas consommer le quota, et on refuse un hôte inconnu ou un gros corps
    avant de compter quoi que ce soit.
    """
    application.add_middleware(
        MiddlewareLimiteDebit,
        limiteur=protections.limiteur,
        limiteur_bloc_48=protections.limiteur_bloc_48,
    )
    application.add_middleware(MiddlewareBlocageEcritures, liste=protections.adresses_bloquees)
    application.add_middleware(MiddlewareTailleCorps, taille_max=parametres.taille_max_corps)
    application.add_middleware(MiddlewareHotesAcceptes, hotes=parametres.hotes_acceptes)
    application.add_middleware(MiddlewareEnTetesSecurite)
