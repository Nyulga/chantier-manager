"""Aucune course entre créations simultanées ne fait dépasser un plafond (ADR 0016)."""

from collections.abc import Iterator
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import Barrier

import pytest
from sqlalchemy.orm import Session, sessionmaker

from app.chantiers.application.creer_chantier import CreerChantier
from app.chantiers.application.plafonds import LIMITE_CHANTIERS
from app.chantiers.infrastructure.sql.unit_of_work import SqlUnitOfWorkChantiers
from app.composition.mapping import metadonnees
from app.shared.application.erreurs import PlafondAtteintError
from app.shared.domain.acteur import Acteur, Role
from app.shared.infrastructure.generateur_uuid7 import GenerateurUuid7
from app.shared.infrastructure.horloge_systeme import HorlogeSysteme
from app.shared.infrastructure.sql.moteur import creer_moteur, creer_usine_sessions
from tests.conftest import url_sqlite
from tests.fabriques.chantiers import un_chantier, une_commande

CHEF = Acteur(Role.CHEF)
# Moins que les 15 connexions du pool (5 + 10 de débordement) : chaque fil a la sienne et
# tous peuvent donc lire le comptage en même temps, comme les requêtes de la production.
CREATIONS_SIMULTANEES = 12
# Ce test prouve le plafond, pas le délai d'attente : sous SQLite, un fil peut attendre le verrou
# plusieurs secondes quand ses concurrents repassent avant lui. Le délai large (en secondes)
# évite qu'un fil ne dépasse celui du pilote (5 s) et ne fasse échouer le test au hasard.
DELAI_ATTENTE_VERROU = 30


@pytest.fixture
def usine_sessions(tmp_path: Path) -> Iterator[sessionmaker[Session]]:
    """Base SQLite jetable, ouverte avec un long délai d'attente du verrou d'écriture."""
    moteur = creer_moteur(f"{url_sqlite(tmp_path)}?timeout={DELAI_ATTENTE_VERROU}")
    metadonnees().create_all(moteur)
    yield creer_usine_sessions(moteur)
    moteur.dispose()


def remplir_jusqu_a_un_de_moins_que_le_plafond(usine: sessionmaker[Session]) -> None:
    with SqlUnitOfWorkChantiers(usine) as uow:
        for numero in range(1, LIMITE_CHANTIERS):
            uow.chantiers.ajouter(un_chantier(numero))
        uow.valider()


def compter_les_chantiers(usine: sessionmaker[Session]) -> int:
    with SqlUnitOfWorkChantiers(usine) as uow:
        return len(uow.chantiers.lister())


def test_des_creations_simultanees_ne_depassent_pas_le_plafond_de_chantiers(
    usine_sessions: sessionmaker[Session],
) -> None:
    remplir_jusqu_a_un_de_moins_que_le_plafond(usine_sessions)
    depart = Barrier(CREATIONS_SIMULTANEES)
    generateur = GenerateurUuid7()

    def creer() -> PlafondAtteintError | None:
        # Chaque fil a son propre Unit of Work, comme chaque requête de la production.
        cas = CreerChantier(SqlUnitOfWorkChantiers(usine_sessions), generateur, HorlogeSysteme())
        depart.wait()
        try:
            cas.executer(une_commande(), CHEF)
        except PlafondAtteintError as erreur:
            return erreur
        return None

    with ThreadPoolExecutor(max_workers=CREATIONS_SIMULTANEES) as fils:
        futurs = [fils.submit(creer) for _ in range(CREATIONS_SIMULTANEES)]
        issues = [futur.result() for futur in futurs]

    # Toute autre erreur lève dans `futur.result()` et fait échouer le test.
    refus = [issue for issue in issues if issue is not None]
    assert compter_les_chantiers(usine_sessions) == LIMITE_CHANTIERS
    assert len(refus) == CREATIONS_SIMULTANEES - 1
