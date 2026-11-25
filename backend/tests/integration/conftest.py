"""Fixtures d'intégration : l'application complète, branchée sur une base SQLite jetable."""

from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient

from app.composition.parametres import Parametres
from app.main import creer_application
from tests.conftest import url_sqlite

HOTE_DE_TEST = "testserver"
SEUIL_LARGE = 100_000
CHEF = {"X-Profil": "chef"}
OUVRIER = {"X-Profil": "ouvrier"}

CHANTIER_A_CREER: dict[str, Any] = {
    "nom": "Rénovation école",
    "adresse": {"voie": "12 rue des Lilas", "code_postal": "69001", "ville": "Lyon"},
    "client": "Mairie fictive",
    "date_debut": "2026-12-01",
    "echeance": "2027-03-31",
    "budget": "125000.50",
}


def parametres_de_test(dossier: Path, **surcharges: Any) -> Parametres:
    """Paramètres d'une application de test : base jetable, hôte du `TestClient`.

    Le `TestClient` s'adresse à l'hôte `testserver`, que les paramètres par défaut (hôtes
    locaux seulement) refusent en 400. Les surcharges permettent à un test de changer
    le reste.
    """
    base: dict[str, Any] = {"url_base": url_sqlite(dossier), "hotes_acceptes": [HOTE_DE_TEST]}
    return Parametres(**{**base, **surcharges})


@pytest.fixture
def client(tmp_path: Path) -> Iterator[TestClient]:
    """Client de l'application complète ; le démarrage applique les migrations sur la base vide.

    La documentation OpenAPI est ouverte, car des tests la lisent, et les seuils de débit
    sont relevés : certains tests écrivent des centaines de fois depuis la même adresse.
    """
    parametres = parametres_de_test(
        tmp_path,
        documentation_exposee=True,
        ecritures_par_minute=SEUIL_LARGE,
        lectures_par_minute=SEUIL_LARGE,
    )
    with TestClient(creer_application(parametres)) as client_http:
        yield client_http


@pytest.fixture
def client_protege(tmp_path: Path) -> Iterator[TestClient]:
    """Client de l'application telle qu'en production : seuils, documentation fermée."""
    with TestClient(creer_application(parametres_de_test(tmp_path))) as client_http:
        yield client_http
