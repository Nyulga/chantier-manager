"""Comportements propres à l'Unit of Work SQL : verrou optimiste et clés étrangères."""

from datetime import UTC, datetime

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, sessionmaker

from app.chantiers.infrastructure.sql.unit_of_work import SqlUnitOfWorkChantiers
from app.etapes.domain.cycle import ActionEtape
from app.etapes.infrastructure.sql.unit_of_work import SqlUnitOfWorkEtapes
from app.shared.domain.acteur import Acteur, Role
from app.shared.domain.erreurs import ConflitVersionError
from tests.unitaires.chantiers.fabriques import un_chantier
from tests.unitaires.etapes.fabriques import ID_CHANTIER, une_etape

OUVRIER = Acteur(Role.OUVRIER)
INSTANT = datetime(2026, 11, 22, 9, 0, tzinfo=UTC)


def preparer_une_etape(usine: sessionmaker[Session]) -> SqlUnitOfWorkEtapes:
    with SqlUnitOfWorkChantiers(usine) as chantiers:
        chantiers.chantiers.ajouter(un_chantier(ID_CHANTIER.int))
        chantiers.valider()
    uow = SqlUnitOfWorkEtapes(usine)
    with uow:
        uow.etapes.ajouter(une_etape())
        uow.valider()
    return uow


def test_deux_modifications_simultanees_d_une_etape_donnent_un_conflit_de_version(
    usine_sessions: sessionmaker[Session],
) -> None:
    preparer_une_etape(usine_sessions)
    premiere, seconde = SqlUnitOfWorkEtapes(usine_sessions), SqlUnitOfWorkEtapes(usine_sessions)
    identifiant = une_etape().id

    with premiere, seconde:
        premiere.etapes.obtenir(identifiant).appliquer(ActionEtape.DEMARRER, OUVRIER, INSTANT)
        seconde.etapes.obtenir(identifiant).appliquer(ActionEtape.DEMARRER, OUVRIER, INSTANT)
        premiere.valider()
        with pytest.raises(ConflitVersionError):
            seconde.valider()


def test_la_base_refuse_une_etape_dont_le_chantier_n_existe_pas(
    usine_sessions: sessionmaker[Session],
) -> None:
    uow = SqlUnitOfWorkEtapes(usine_sessions)

    with uow, pytest.raises(IntegrityError):
        uow.etapes.ajouter(une_etape())
        uow.valider()


def test_un_uow_est_reutilisable_apres_une_erreur(usine_sessions: sessionmaker[Session]) -> None:
    uow = preparer_une_etape(usine_sessions)

    with uow, pytest.raises(IntegrityError):
        uow.etapes.ajouter(une_etape())
        uow.valider()
    with uow:
        etapes = uow.etapes.lister_par_chantiers([ID_CHANTIER])

    assert len(etapes) == 1
