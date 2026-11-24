"""Assemblage des protections de la démo publique : limite de débit, pièges et middlewares.

Le limiteur et la liste d'adresses bloquées sont créés une seule fois par application :
les middlewares et les routes pièges doivent partager les mêmes instances, sinon une adresse
piégée par une route ne serait pas bloquée par le middleware. Ce fichier ne fait
qu'assembler (règle 06) ; les règles sont dans `shared`.
"""

from dataclasses import dataclass

from fastapi import FastAPI

from app.composition.parametres import Parametres
from app.shared.api.blocage_ecritures import MiddlewareBlocageEcritures
from app.shared.api.en_tetes_securite import MiddlewareEnTetesSecurite
from app.shared.api.hotes_acceptes import MiddlewareHotesAcceptes
from app.shared.api.limite_debit import MiddlewareLimiteDebit
from app.shared.api.taille_corps import MiddlewareTailleCorps
from app.shared.application.limites_debit import DUREE_BLOCAGE_PIEGE, FENETRE_DEBIT
from app.shared.application.ports import CategorieAcces, LimiteurDebit, ListeAdressesBloquees
from app.shared.infrastructure.adresses_bloquees_memoire import MemoireListeAdressesBloquees
from app.shared.infrastructure.horloge_systeme import HorlogeSysteme
from app.shared.infrastructure.limiteur_debit_memoire import MemoireLimiteurDebit


@dataclass(frozen=True)
class Protections:
    """Les deux états partagés des protections : le limiteur et la liste des adresses bloquées."""

    limiteur: LimiteurDebit
    adresses_bloquees: ListeAdressesBloquees


def creer_protections(parametres: Parametres) -> Protections:
    """Crée le limiteur et la liste d'adresses bloquées, en mémoire (ADR 0015)."""
    horloge = HorlogeSysteme()
    seuils = {
        CategorieAcces.ECRITURE: parametres.ecritures_par_minute,
        CategorieAcces.LECTURE: parametres.lectures_par_minute,
    }
    return Protections(
        limiteur=MemoireLimiteurDebit(horloge, seuils, FENETRE_DEBIT),
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
    application.add_middleware(MiddlewareLimiteDebit, limiteur=protections.limiteur)
    application.add_middleware(MiddlewareBlocageEcritures, liste=protections.adresses_bloquees)
    application.add_middleware(MiddlewareTailleCorps, taille_max=parametres.taille_max_corps)
    application.add_middleware(MiddlewareHotesAcceptes, hotes=parametres.hotes_acceptes)
    application.add_middleware(MiddlewareEnTetesSecurite)
