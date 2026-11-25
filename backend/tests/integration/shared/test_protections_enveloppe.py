"""Protections branchées sur l'application réelle : taille, hôte, en-têtes, documentation, routes.

Elles prouvent que `creer_application` empile bien les middlewares avec les paramètres lus,
et qu'une réponse de refus porte elle aussi les en-têtes de sécurité (le middleware des
en-têtes est le plus extérieur).
"""

from http import HTTPStatus

import pytest
from fastapi.testclient import TestClient

from app.composition.parametres import TAILLE_MAX_CORPS
from app.shared.api.en_tetes_securite import EN_TETES_SECURITE
from tests.integration.conftest import CHANTIER_A_CREER, CHEF

TYPE_PROBLEME = "application/problem+json"
EN_TETES_JSON = {**CHEF, "Content-Type": "application/json"}


def test_un_corps_de_plus_de_64_kio_est_refuse_en_413(client: TestClient) -> None:
    reponse = client.post(
        "/api/chantiers", content=b" " * (TAILLE_MAX_CORPS + 1), headers=EN_TETES_JSON
    )

    assert reponse.status_code == HTTPStatus.CONTENT_TOO_LARGE
    assert reponse.headers["content-type"] == TYPE_PROBLEME


def test_un_corps_normal_n_est_pas_refuse(client: TestClient) -> None:
    reponse = client.post("/api/chantiers", json=CHANTIER_A_CREER, headers=CHEF)

    assert reponse.status_code == HTTPStatus.CREATED


def test_un_hote_inconnu_est_refuse_en_400_au_format_rfc_9457(client: TestClient) -> None:
    reponse = client.get("/api/chantiers", headers={**CHEF, "Host": "intrus.example"})

    assert reponse.status_code == HTTPStatus.BAD_REQUEST
    assert reponse.headers["content-type"] == TYPE_PROBLEME
    assert "intrus.example" not in reponse.text


@pytest.mark.parametrize(
    ("chemin", "statut"),
    [("/api/health", HTTPStatus.OK), ("/api/rien-du-tout", HTTPStatus.NOT_FOUND)],
)
def test_les_en_tetes_de_securite_sont_sur_les_reponses_normales_et_les_404(
    client: TestClient, chemin: str, statut: HTTPStatus
) -> None:
    reponse = client.get(chemin)

    assert reponse.status_code == statut
    for nom, valeur in EN_TETES_SECURITE.items():
        assert reponse.headers[nom] == valeur


def test_les_en_tetes_de_securite_sont_aussi_sur_un_refus_de_hote(client: TestClient) -> None:
    reponse = client.get("/api/health", headers={"Host": "intrus.example"})

    assert reponse.status_code == HTTPStatus.BAD_REQUEST
    assert reponse.headers["x-frame-options"] == "DENY"


@pytest.mark.parametrize("chemin", ["/api/docs", "/api/openapi.json"])
def test_la_documentation_est_fermee_quand_elle_n_est_pas_exposee(
    client_protege: TestClient, chemin: str
) -> None:
    assert client_protege.get(chemin).status_code == HTTPStatus.NOT_FOUND


@pytest.mark.parametrize("chemin", ["/api/docs", "/api/openapi.json"])
def test_la_documentation_est_ouverte_quand_elle_est_exposee(
    client: TestClient, chemin: str
) -> None:
    assert client.get(chemin).status_code == HTTPStatus.OK


def test_une_barre_oblique_finale_donne_un_404_sans_redirection(client: TestClient) -> None:
    reponse = client.get("/api/chantiers/", headers=CHEF, follow_redirects=False)

    assert reponse.status_code == HTTPStatus.NOT_FOUND
    assert "location" not in reponse.headers
