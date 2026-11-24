"""Middleware de limite de débit : 429 avec `Retry-After`, catégories, sonde de santé exemptée."""

from datetime import UTC, datetime, timedelta
from http import HTTPStatus

import pytest
from fastapi.testclient import TestClient

from app.shared.api.limite_debit import MiddlewareLimiteDebit
from app.shared.application.ports import CategorieAcces
from app.shared.infrastructure.limiteur_debit_memoire import MemoireLimiteurDebit
from app.shared.infrastructure.memoire.horloge_avancable import HorlogeAvancable
from tests.integration.shared.petite_application import une_petite_application

FENETRE = timedelta(seconds=60)
SEUIL_ECRITURES = 2
SEUIL_LECTURES = 3
MESSAGE = "Trop de demandes. Réessaie dans quelques instants."


def un_client() -> tuple[TestClient, list[str], HorlogeAvancable]:
    horloge = HorlogeAvancable(datetime(2026, 11, 24, 9, 0, tzinfo=UTC))
    limiteur = MemoireLimiteurDebit(
        horloge,
        {CategorieAcces.ECRITURE: SEUIL_ECRITURES, CategorieAcces.LECTURE: SEUIL_LECTURES},
        FENETRE,
        cles_max=10,
    )
    application, appels = une_petite_application()
    application.add_middleware(MiddlewareLimiteDebit, limiteur=limiteur)
    return TestClient(application), appels, horloge


def test_une_ecriture_au_dela_du_seuil_est_refusee_en_429_sans_appeler_la_route() -> None:
    client, appels, _ = un_client()
    for _ in range(SEUIL_ECRITURES):
        client.post("/api/ressource")

    reponse = client.post("/api/ressource")

    assert reponse.status_code == HTTPStatus.TOO_MANY_REQUESTS
    assert reponse.headers["retry-after"] == "60"
    assert reponse.headers["content-type"] == "application/problem+json"
    assert reponse.json()["detail"] == MESSAGE
    assert len(appels) == SEUIL_ECRITURES


@pytest.mark.parametrize("methode", ["POST", "PUT", "PATCH", "DELETE"])
def test_les_methodes_qui_modifient_comptent_comme_des_ecritures(methode: str) -> None:
    client, _, _ = un_client()
    for _ in range(SEUIL_ECRITURES):
        client.request(methode, "/api/ressource")

    reponse = client.request(methode, "/api/ressource")

    assert reponse.status_code == HTTPStatus.TOO_MANY_REQUESTS


@pytest.mark.parametrize("methode", ["GET", "HEAD"])
def test_les_autres_methodes_comptent_comme_des_lectures(methode: str) -> None:
    client, _, _ = un_client()
    for _ in range(SEUIL_LECTURES):
        client.request(methode, "/api/ressource")

    reponse = client.request(methode, "/api/ressource")

    assert reponse.status_code == HTTPStatus.TOO_MANY_REQUESTS


def test_les_lectures_et_les_ecritures_sont_comptees_a_part() -> None:
    client, _, _ = un_client()
    for _ in range(SEUIL_LECTURES):
        client.get("/api/ressource")

    reponse = client.post("/api/ressource")

    assert reponse.status_code == HTTPStatus.OK


def test_l_acces_est_de_nouveau_permis_une_fois_le_delai_ecoule() -> None:
    client, _, horloge = un_client()
    for _ in range(SEUIL_ECRITURES + 1):
        client.post("/api/ressource")
    horloge.avancer(FENETRE)

    reponse = client.post("/api/ressource")

    assert reponse.status_code == HTTPStatus.OK


def test_la_sonde_de_sante_n_est_jamais_limitee() -> None:
    client, _, _ = un_client()
    for _ in range(SEUIL_LECTURES * 3):
        client.get("/api/health")

    reponse = client.get("/api/health")

    assert reponse.status_code == HTTPStatus.OK


def test_les_chemins_hors_de_l_api_ne_sont_pas_limites() -> None:
    client, _, _ = un_client()
    for _ in range(SEUIL_LECTURES * 3):
        client.get("/hors-api")

    reponse = client.get("/hors-api")

    assert reponse.status_code == HTTPStatus.OK


def test_chaque_adresse_a_son_propre_compte() -> None:
    client, _, _ = un_client()
    for _ in range(SEUIL_ECRITURES + 1):
        client.post("/api/ressource")
    autre = TestClient(client.app, client=("203.0.113.9", 5000))

    reponse = autre.post("/api/ressource")

    assert reponse.status_code == HTTPStatus.OK
