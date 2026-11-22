"""Route de santé `/api/health` : réponse, méthodes acceptées et description OpenAPI."""

from http import HTTPStatus

from fastapi.testclient import TestClient

from app.main import creer_application


def test_la_route_sante_repond_ok() -> None:
    client = TestClient(creer_application())

    reponse = client.get("/api/health")

    assert reponse.status_code == HTTPStatus.OK
    assert reponse.json() == {"statut": "ok"}


def test_la_route_sante_refuse_les_methodes_autres_que_get() -> None:
    client = TestClient(creer_application())

    reponse = client.post("/api/health")

    assert reponse.status_code == HTTPStatus.METHOD_NOT_ALLOWED


def test_le_schema_openapi_decrit_la_route_sante() -> None:
    client = TestClient(creer_application())

    schema = client.get("/api/openapi.json").json()

    assert "/api/health" in schema["paths"]
