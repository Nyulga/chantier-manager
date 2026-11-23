"""Enregistrement d'étapes dans une transaction, partagé par les contrats du repository."""

from app.etapes.application.ports import UnitOfWorkEtapes
from app.etapes.domain.etape import Etape


def enregistrer(uow: UnitOfWorkEtapes, *etapes: Etape) -> None:
    with uow:
        for etape in etapes:
            uow.etapes.ajouter(etape)
        uow.valider()
