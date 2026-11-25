"""En-têtes de sécurité : posés sur toutes les réponses de l'API, erreurs comprises."""

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.shared.api.en_tetes_securite import EN_TETES_SECURITE, MiddlewareEnTetesSecurite
from tests.integration.shared.petite_application import une_petite_application

CADDYFILE = Path(__file__).resolve().parents[4] / "deploy" / "Caddyfile.extrait"


def un_client() -> TestClient:
    application, _ = une_petite_application()
    application.add_middleware(MiddlewareEnTetesSecurite)
    return TestClient(application, raise_server_exceptions=False)


@pytest.mark.parametrize(
    ("methode", "chemin"),
    [
        ("GET", "/api/ressource"),
        ("GET", "/api/inconnue"),
        ("DELETE", "/api/health"),
        ("POST", "/api/ressource"),
        ("GET", "/api/erreur"),
    ],
)
def test_toutes_les_reponses_portent_les_en_tetes_de_securite(methode: str, chemin: str) -> None:
    reponse = un_client().request(methode, chemin)

    assert {nom: reponse.headers.get(nom) for nom in EN_TETES_SECURITE} == EN_TETES_SECURITE


def test_les_en_tetes_sont_les_memes_que_ceux_du_caddyfile() -> None:
    lignes = {ligne.strip() for ligne in CADDYFILE.read_text(encoding="utf-8").splitlines()}

    absents = {
        nom
        for nom, valeur in EN_TETES_SECURITE.items()
        if f"{nom} {valeur}" not in lignes and f'{nom} "{valeur}"' not in lignes
    }

    assert absents == set()


def test_le_demarrage_de_l_application_traverse_le_middleware() -> None:
    application, _ = une_petite_application()
    application.add_middleware(MiddlewareEnTetesSecurite)

    with TestClient(application) as client:
        reponse = client.get("/api/health")

    assert reponse.headers["X-Frame-Options"] == "DENY"
