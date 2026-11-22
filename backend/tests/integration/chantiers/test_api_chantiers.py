"""Routes des chantiers : nominal, droits, budget masqué, 404, 422 et profil absent."""

from copy import deepcopy
from http import HTTPStatus
from typing import Any
from uuid import UUID

import pytest
from fastapi.testclient import TestClient

from tests.integration.conftest import CHANTIER_A_CREER, CHEF, OUVRIER

UUID_VERSION_7 = 7


def creer(client: TestClient, corps: dict[str, Any] | None = None) -> dict[str, Any]:
    reponse = client.post("/api/chantiers", json=corps or CHANTIER_A_CREER, headers=CHEF)
    assert reponse.status_code == HTTPStatus.CREATED
    resultat: dict[str, Any] = reponse.json()
    return resultat


def test_un_chef_cree_un_chantier_sans_avancement(client: TestClient) -> None:
    chantier = creer(client)

    assert UUID(chantier.pop("id")).version == UUID_VERSION_7
    assert chantier == {
        "nom": "Rénovation école",
        "adresse": {"voie": "12 rue des Lilas", "code_postal": "69001", "ville": "Lyon"},
        "client": "Mairie fictive",
        "date_debut": "2026-12-01",
        "echeance": "2027-03-31",
        "budget": "125000.50",
        "avancement": 0,
        "peut_ajouter_etape": True,
    }


def test_un_ouvrier_ne_peut_pas_creer_de_chantier(client: TestClient) -> None:
    reponse = client.post("/api/chantiers", json=CHANTIER_A_CREER, headers=OUVRIER)

    assert reponse.status_code == HTTPStatus.FORBIDDEN


def test_les_espaces_autour_de_la_saisie_sont_retires(client: TestClient) -> None:
    corps = deepcopy(CHANTIER_A_CREER)
    corps["nom"] = "  Rénovation école  "

    chantier = creer(client, corps)

    assert chantier["nom"] == "Rénovation école"


@pytest.mark.parametrize(
    ("champ", "valeur"),
    [
        ("echeance", "2026-11-30"),
        ("nom", "   "),
        ("budget", "-1"),
        ("budget", "10.123"),
        ("adresse", {"voie": "", "code_postal": "69001", "ville": "Lyon"}),
        ("inconnu", "valeur"),
    ],
)
def test_un_chantier_invalide_est_refuse_avec_un_422(
    client: TestClient, champ: str, valeur: object
) -> None:
    corps = {**CHANTIER_A_CREER, champ: valeur}

    reponse = client.post("/api/chantiers", json=corps, headers=CHEF)

    assert reponse.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert reponse.headers["content-type"] == "application/problem+json"


def test_la_liste_contient_les_chantiers_dans_l_ordre_de_creation(client: TestClient) -> None:
    premier = creer(client)
    second = creer(client, {**CHANTIER_A_CREER, "nom": "Second"})

    reponse = client.get("/api/chantiers", headers=CHEF)

    assert [chantier["id"] for chantier in reponse.json()] == [premier["id"], second["id"]]


def test_l_ouvrier_voit_les_chantiers_sans_budget_et_sans_droit_d_ajout(
    client: TestClient,
) -> None:
    creer(client)

    liste = client.get("/api/chantiers", headers=OUVRIER).json()

    assert liste[0]["budget"] is None
    assert liste[0]["peut_ajouter_etape"] is False


def test_le_detail_d_un_chantier_est_renvoye_au_chef_avec_son_budget(client: TestClient) -> None:
    chantier = creer(client)

    reponse = client.get(f"/api/chantiers/{chantier['id']}", headers=CHEF)

    assert reponse.status_code == HTTPStatus.OK
    assert reponse.json() == chantier


def test_le_detail_masque_le_budget_a_l_ouvrier(client: TestClient) -> None:
    chantier = creer(client)

    reponse = client.get(f"/api/chantiers/{chantier['id']}", headers=OUVRIER)

    assert reponse.json()["budget"] is None


def test_un_chantier_inexistant_donne_un_404(client: TestClient) -> None:
    reponse = client.get(f"/api/chantiers/{UUID(int=1)}", headers=CHEF)

    assert reponse.status_code == HTTPStatus.NOT_FOUND
    assert reponse.json()["detail"] == "Chantier introuvable."


@pytest.mark.parametrize("methode", ["get", "post"])
def test_sans_profil_les_routes_des_chantiers_donnent_un_400(
    client: TestClient, methode: str
) -> None:
    reponse = client.request(methode, "/api/chantiers", json=CHANTIER_A_CREER)

    assert reponse.status_code == HTTPStatus.BAD_REQUEST
