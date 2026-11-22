"""Fixtures des tests de contrat : chaque port est joué sur le fake mémoire et sur SQL."""

from uuid import UUID

import pytest
from sqlalchemy.orm import Session, sessionmaker

from app.chantiers.application.ports import UnitOfWorkChantiers
from app.chantiers.infrastructure.memoire.unit_of_work import MemoireUnitOfWorkChantiers
from app.chantiers.infrastructure.sql.unit_of_work import SqlUnitOfWorkChantiers
from app.etapes.application.ports import UnitOfWorkEtapes
from app.etapes.infrastructure.memoire.unit_of_work import MemoireUnitOfWorkEtapes
from app.etapes.infrastructure.sql.unit_of_work import SqlUnitOfWorkEtapes
from tests.unitaires.chantiers.fabriques import un_chantier
from tests.unitaires.etapes.fabriques import ID_CHANTIER

IMPLEMENTATIONS = ["memoire", "sql"]
AUTRE_CHANTIER = UUID(int=ID_CHANTIER.int + 1)


@pytest.fixture(params=IMPLEMENTATIONS)
def uow_chantiers(request: pytest.FixtureRequest) -> UnitOfWorkChantiers:
    """Unit of Work des chantiers : une fois en mémoire, une fois sur SQLite."""
    if request.param == "memoire":
        return MemoireUnitOfWorkChantiers()
    usine: sessionmaker[Session] = request.getfixturevalue("usine_sessions")
    return SqlUnitOfWorkChantiers(usine)


@pytest.fixture(params=IMPLEMENTATIONS)
def uow_etapes(request: pytest.FixtureRequest) -> UnitOfWorkEtapes:
    """Unit of Work des étapes, avec deux chantiers existants pour la clé étrangère SQL."""
    if request.param == "memoire":
        return MemoireUnitOfWorkEtapes()
    usine: sessionmaker[Session] = request.getfixturevalue("usine_sessions")
    with SqlUnitOfWorkChantiers(usine) as chantiers:
        chantiers.chantiers.ajouter(un_chantier(ID_CHANTIER.int))
        chantiers.chantiers.ajouter(un_chantier(AUTRE_CHANTIER.int))
        chantiers.valider()
    return SqlUnitOfWorkEtapes(usine)
