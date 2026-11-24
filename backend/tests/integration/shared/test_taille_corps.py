"""Limite de taille des corps : refus en 413 sur `Content-Length` et sur un corps découpé."""

from collections.abc import Iterator
from http import HTTPStatus

from fastapi.testclient import TestClient
from starlette.types import Receive, Scope, Send

from app.shared.api.taille_corps import MiddlewareTailleCorps
from tests.integration.shared.petite_application import une_petite_application

TAILLE_MAX = 100


def un_client() -> tuple[TestClient, list[str]]:
    application, appels = une_petite_application()
    application.add_middleware(MiddlewareTailleCorps, taille_max=TAILLE_MAX)
    return TestClient(application), appels


def morceaux(nombre: int, taille: int) -> Iterator[bytes]:
    for _ in range(nombre):
        yield b"x" * taille


def test_un_corps_a_la_limite_est_accepte() -> None:
    client, _ = un_client()

    reponse = client.post("/api/ressource", content=b"x" * TAILLE_MAX)

    assert reponse.status_code == HTTPStatus.OK
    assert reponse.json() == {"octets": TAILLE_MAX}


def test_un_content_length_au_dela_de_la_limite_est_refuse_sans_appeler_la_route() -> None:
    client, appels = un_client()

    reponse = client.post("/api/ressource", content=b"x" * (TAILLE_MAX + 1))

    assert reponse.status_code == HTTPStatus.CONTENT_TOO_LARGE
    assert reponse.headers["content-type"] == "application/problem+json"
    assert reponse.json()["status"] == HTTPStatus.CONTENT_TOO_LARGE
    assert appels == []


def test_un_corps_decoupe_est_coupe_des_que_la_limite_est_franchie() -> None:
    client, _ = un_client()

    reponse = client.post("/api/ressource", content=morceaux(nombre=5, taille=40))

    assert reponse.status_code == HTTPStatus.CONTENT_TOO_LARGE
    assert reponse.json()["detail"] == "Le corps de la requête est trop volumineux."


def test_un_corps_decoupe_sous_la_limite_est_accepte() -> None:
    client, _ = un_client()

    reponse = client.post("/api/ressource", content=morceaux(nombre=2, taille=40))

    assert reponse.status_code == HTTPStatus.OK
    assert reponse.json() == {"octets": 80}


def test_le_demarrage_de_l_application_traverse_le_middleware() -> None:
    application, _ = une_petite_application()
    application.add_middleware(MiddlewareTailleCorps, taille_max=TAILLE_MAX)

    with TestClient(application) as client:
        reponse = client.get("/api/health")

    assert reponse.status_code == HTTPStatus.OK


def test_une_erreur_sans_rapport_avec_la_taille_n_est_pas_masquee() -> None:
    application, _ = une_petite_application()
    application.add_middleware(MiddlewareTailleCorps, taille_max=TAILLE_MAX)

    reponse = TestClient(application, raise_server_exceptions=False).get("/api/erreur")

    assert reponse.status_code == HTTPStatus.INTERNAL_SERVER_ERROR


def test_un_content_length_illisible_est_ignore_et_les_octets_recus_comptent() -> None:
    client, _ = un_client()

    reponse = client.get("/api/ressource", headers={"content-length": "abc"})

    assert reponse.status_code == HTTPStatus.OK


async def application_qui_repond_apres_la_coupure(
    _scope: Scope, receive: Receive, send: Send
) -> None:
    """Application qui lit tout le corps, insiste après la coupure, puis répond 200."""
    message = await receive()
    while message["type"] == "http.request":
        message = await receive()
    await receive()
    await send({"type": "http.response.start", "status": 200, "headers": []})
    await send({"type": "http.response.body", "body": b"ok"})


def test_la_reponse_d_une_application_qui_survit_a_la_coupure_est_remplacee_par_le_413() -> None:
    client = TestClient(MiddlewareTailleCorps(application_qui_repond_apres_la_coupure, TAILLE_MAX))

    reponse = client.post("/api/ressource", content=morceaux(nombre=5, taille=40))

    assert reponse.status_code == HTTPStatus.CONTENT_TOO_LARGE
