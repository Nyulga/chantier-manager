"""Fixtures d'intégration : l'application complète, branchée sur une base SQLite jetable."""

from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.composition.parametres import Parametres
from app.main import creer_application
from tests.conftest import url_sqlite

CHEF = {"X-Profil": "chef"}
OUVRIER = {"X-Profil": "ouvrier"}

CHANTIER_A_CREER = {
    "nom": "Rénovation école",
    "adresse": {"voie": "12 rue des Lilas", "code_postal": "69001", "ville": "Lyon"},
    "client": "Mairie fictive",
    "date_debut": "2026-12-01",
    "echeance": "2027-03-31",
    "budget": "125000.50",
}


@pytest.fixture
def client(tmp_path: Path) -> Iterator[TestClient]:
    """Client de l'application complète ; le démarrage applique les migrations sur la base vide."""
    application = creer_application(Parametres(url_base=url_sqlite(tmp_path)))
    with TestClient(application) as client_http:
        yield client_http
