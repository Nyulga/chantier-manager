"""Fixtures des tests de contrat : chaque port est joué sur chacune de ses implémentations.

Les ports de persistance le sont sur le fake mémoire et sur SQL ; l'horloge, le
générateur d'identifiants et le fournisseur de résumés, sur leur implémentation
réelle et sur celle des tests (principe de Liskov, règle 00).
"""

from datetime import UTC, datetime
from uuid import UUID

import pytest
from sqlalchemy.orm import Session, sessionmaker

from app.chantiers.application.ports import FournisseurResumeEtapes, UnitOfWorkChantiers
from app.chantiers.infrastructure.memoire.resume_etapes_fixe import ResumeEtapesFixe
from app.chantiers.infrastructure.memoire.unit_of_work import MemoireUnitOfWorkChantiers
from app.chantiers.infrastructure.sql.unit_of_work import SqlUnitOfWorkChantiers
from app.composition.resume_etapes import ResumeEtapesDepuisEtapes
from app.etapes.application import CalculerResumesEtapes
from app.etapes.application.ports import UnitOfWorkEtapes
from app.etapes.infrastructure.memoire.unit_of_work import MemoireUnitOfWorkEtapes
from app.etapes.infrastructure.sql.unit_of_work import SqlUnitOfWorkEtapes
from app.shared.application.ports import GenerateurId, Horloge
from app.shared.infrastructure.generateur_uuid7 import GenerateurUuid7
from app.shared.infrastructure.horloge_systeme import HorlogeSysteme
from app.shared.infrastructure.memoire.generateur_id_previsible import GenerateurIdPrevisible
from app.shared.infrastructure.memoire.horloge_fixe import HorlogeFixe
from tests.unitaires.chantiers.fabriques import un_chantier
from tests.unitaires.etapes.fabriques import ID_CHANTIER

IMPLEMENTATIONS = ["memoire", "sql"]
# Un soir d'hiver, 23 h 30 en UTC : il est déjà le lendemain à Paris.
INSTANT_FIXE = datetime(2026, 11, 22, 23, 30, tzinfo=UTC)
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


@pytest.fixture(params=["systeme", "fixe"])
def horloge(request: pytest.FixtureRequest) -> Horloge:
    """Horloge : celle du système, puis l'horloge figée des tests."""
    if request.param == "systeme":
        return HorlogeSysteme()
    return HorlogeFixe(INSTANT_FIXE)


@pytest.fixture(params=["uuid7", "previsible"])
def generateur_id(request: pytest.FixtureRequest) -> GenerateurId:
    """Générateur d'identifiants : UUID v7 de production, puis identifiants prévisibles."""
    if request.param == "uuid7":
        return GenerateurUuid7()
    return GenerateurIdPrevisible()


@pytest.fixture(params=["fixe", "depuis_etapes"])
def fournisseur_resume(request: pytest.FixtureRequest) -> FournisseurResumeEtapes:
    """Fournisseur de résumés : celui des tests de chantiers, puis l'adaptateur réel.

    Aucun des deux ne connaît d'étape : le contrat porte sur la forme du résultat,
    pas sur le calcul, que les tests d'étapes vérifient déjà.
    """
    if request.param == "fixe":
        return ResumeEtapesFixe({})
    return ResumeEtapesDepuisEtapes(CalculerResumesEtapes(MemoireUnitOfWorkEtapes()))
