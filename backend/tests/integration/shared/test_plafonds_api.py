"""Plafonds de volume et textes propres, vus de l'API : 409 au plafond, 422 sur un caractère nul."""

from http import HTTPStatus

from fastapi.testclient import TestClient

from app.chantiers.application.plafonds import LIMITE_CHANTIERS, MESSAGE_LIMITE_CHANTIERS
from app.etapes.application.plafonds import LIMITE_ETAPES_PAR_CHANTIER, MESSAGE_LIMITE_ETAPES
from tests.integration.conftest import CHANTIER_A_CREER, CHEF
from tests.integration.etapes.scenario import ajouter_etape, creer_chantier

TYPE_PROBLEME = "application/problem+json"


def test_le_chantier_au_dela_du_plafond_est_refuse_en_409(client: TestClient) -> None:
    for _ in range(LIMITE_CHANTIERS):
        creer_chantier(client)

    reponse = client.post("/api/chantiers", json=CHANTIER_A_CREER, headers=CHEF)

    assert reponse.status_code == HTTPStatus.CONFLICT
    assert reponse.headers["content-type"] == TYPE_PROBLEME
    assert reponse.json()["detail"] == MESSAGE_LIMITE_CHANTIERS


def test_l_etape_au_dela_du_plafond_est_refusee_en_409(client: TestClient) -> None:
    chantier_id = creer_chantier(client)
    for _ in range(LIMITE_ETAPES_PAR_CHANTIER):
        ajouter_etape(client, chantier_id)

    reponse = client.post(
        f"/api/chantiers/{chantier_id}/etapes", json={"titre": "Une de trop"}, headers=CHEF
    )

    assert reponse.status_code == HTTPStatus.CONFLICT
    assert reponse.json()["detail"] == MESSAGE_LIMITE_ETAPES


def test_un_caractere_nul_dans_le_nom_est_refuse_en_422_sur_le_champ(client: TestClient) -> None:
    corps = {**CHANTIER_A_CREER, "nom": "a\u0000b"}

    reponse = client.post("/api/chantiers", json=corps, headers=CHEF)

    assert reponse.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert [erreur["champ"] for erreur in reponse.json()["erreurs"]] == ["nom"]


def test_un_budget_en_nombre_json_est_refuse_en_422_sur_le_champ(client: TestClient) -> None:
    corps = {**CHANTIER_A_CREER, "budget": 1234.5}

    reponse = client.post("/api/chantiers", json=corps, headers=CHEF)

    assert reponse.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert reponse.json()["erreurs"] == [
        {"champ": "budget", "message": "Ce champ doit être un montant valide."}
    ]


def test_un_budget_en_texte_decimal_est_accepte(client: TestClient) -> None:
    corps = {**CHANTIER_A_CREER, "budget": "1234.50"}

    reponse = client.post("/api/chantiers", json=corps, headers=CHEF)

    assert reponse.status_code == HTTPStatus.CREATED
    assert reponse.json()["budget"] == "1234.50"
