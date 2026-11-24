"""Route de santé `/api/health` : réponse, méthodes acceptées et description OpenAPI."""

from http import HTTPStatus

from fastapi.testclient import TestClient


def test_la_route_sante_repond_ok(client: TestClient) -> None:
    reponse = client.get("/api/health")

    assert reponse.status_code == HTTPStatus.OK
    assert reponse.json() == {"statut": "ok"}


def test_la_route_sante_repond_200_sans_corps_a_head(client: TestClient) -> None:
    reponse = client.head("/api/health")

    assert reponse.status_code == HTTPStatus.OK
    assert reponse.content == b""


def test_la_route_sante_refuse_les_methodes_autres_que_get(client: TestClient) -> None:
    reponse = client.post("/api/health")

    assert reponse.status_code == HTTPStatus.METHOD_NOT_ALLOWED


def test_le_schema_openapi_decrit_la_route_sante(client: TestClient) -> None:
    schema = client.get("/api/openapi.json").json()

    assert "/api/health" in schema["paths"]
