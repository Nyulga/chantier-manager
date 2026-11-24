"""Hôtes acceptés : un en-tête `Host` absent ou inconnu est refusé en 400, au format RFC 9457."""

import asyncio
from http import HTTPStatus

import pytest
from fastapi.testclient import TestClient
from starlette.types import Message, Receive, Scope, Send

from app.shared.api.en_tetes_securite import EN_TETES_SECURITE, MiddlewareEnTetesSecurite
from app.shared.api.hotes_acceptes import MiddlewareHotesAcceptes
from tests.integration.shared.petite_application import une_petite_application

HOTES = ["chantier.exemple.test", "127.0.0.1"]


def un_client() -> tuple[TestClient, list[str]]:
    application, appels = une_petite_application()
    application.add_middleware(MiddlewareHotesAcceptes, hotes=HOTES)
    return TestClient(application), appels


@pytest.mark.parametrize(
    "hote",
    [
        "chantier.exemple.test",
        "CHANTIER.Exemple.TEST",
        "chantier.exemple.test:8000",
        "127.0.0.1:80",
    ],
)
def test_un_hote_de_la_liste_est_accepte_sans_tenir_compte_de_la_casse_ni_du_port(
    hote: str,
) -> None:
    client, _ = un_client()

    reponse = client.get("/api/ressource", headers={"host": hote})

    assert reponse.status_code == HTTPStatus.OK


@pytest.mark.parametrize("hote", ["pirate.invalid", "chantier.exemple.test.pirate.invalid", ""])
def test_un_hote_inconnu_est_refuse_en_400_sans_le_recopier_et_sans_appeler_la_route(
    hote: str,
) -> None:
    client, appels = un_client()

    reponse = client.get("/api/ressource", headers={"host": hote})

    assert reponse.status_code == HTTPStatus.BAD_REQUEST
    assert reponse.headers["content-type"] == "application/problem+json"
    assert reponse.json()["detail"] == "Hôte non reconnu."
    assert hote not in reponse.text or hote == ""
    assert appels == []


async def application_brute(scope: Scope, _receive: Receive, send: Send) -> None:
    """Application qui répond 200 quoi qu'il arrive, même sans en-tête `Host`."""
    await send({"type": "http.response.start", "status": 200, "headers": []})
    await send({"type": "http.response.body", "body": b""})


def test_un_hote_absent_est_refuse_en_400() -> None:
    envoyes: list[Message] = []

    async def recevoir() -> Message:
        return {"type": "http.request", "body": b""}

    async def envoyer(message: Message) -> None:
        envoyes.append(message)

    scope: Scope = {"type": "http", "method": "GET", "path": "/api/ressource", "headers": []}

    asyncio.run(MiddlewareHotesAcceptes(application_brute, HOTES)(scope, recevoir, envoyer))

    assert envoyes[0]["status"] == HTTPStatus.BAD_REQUEST


def test_un_hote_ipv6_est_compare_sans_son_port() -> None:
    client = TestClient(MiddlewareHotesAcceptes(application_brute, ["::1"]))

    reponse = client.get("/api/ressource", headers={"host": "[::1]:8000"})

    assert reponse.status_code == HTTPStatus.OK


def test_le_demarrage_de_l_application_n_est_pas_filtre() -> None:
    application, _ = une_petite_application()
    application.add_middleware(MiddlewareHotesAcceptes, hotes=HOTES)

    with TestClient(application) as client:
        reponse = client.get("/api/health", headers={"host": "127.0.0.1"})

    assert reponse.status_code == HTTPStatus.OK


def test_le_refus_recoit_les_en_tetes_de_securite_quand_ils_sont_a_l_exterieur() -> None:
    application, _ = une_petite_application()
    application.add_middleware(MiddlewareHotesAcceptes, hotes=HOTES)
    application.add_middleware(MiddlewareEnTetesSecurite)

    reponse = TestClient(application).get("/api/ressource", headers={"host": "pirate.invalid"})

    assert reponse.status_code == HTTPStatus.BAD_REQUEST
    assert {nom: reponse.headers.get(nom) for nom in EN_TETES_SECURITE} == EN_TETES_SECURITE
