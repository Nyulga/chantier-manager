"""Adresses bloquées : écritures refusées en 403 neutre, lectures et sonde permises."""

from datetime import UTC, datetime, timedelta
from http import HTTPStatus

import pytest
from fastapi.testclient import TestClient

from app.shared.api.blocage_ecritures import MiddlewareBlocageEcritures
from app.shared.infrastructure.adresses_bloquees_memoire import MemoireListeAdressesBloquees
from app.shared.infrastructure.memoire.horloge_avancable import HorlogeAvancable
from tests.integration.shared.petite_application import une_petite_application

ADRESSE_BLOQUEE = "198.51.100.7"
ADRESSE_LIBRE = "203.0.113.9"
MESSAGE_NEUTRE = "Cette action n'est pas permise."


def un_client(adresse: str) -> tuple[TestClient, list[str]]:
    horloge = HorlogeAvancable(datetime(2026, 11, 24, 9, 0, tzinfo=UTC))
    liste = MemoireListeAdressesBloquees(horloge, timedelta(hours=1))
    liste.bloquer(ADRESSE_BLOQUEE)
    application, appels = une_petite_application()
    application.add_middleware(MiddlewareBlocageEcritures, liste=liste)
    return TestClient(application, client=(adresse, 5000)), appels


@pytest.mark.parametrize("methode", ["POST", "PUT", "PATCH", "DELETE"])
def test_une_adresse_bloquee_ne_peut_pas_ecrire_et_la_route_n_est_pas_appelee(
    methode: str,
) -> None:
    client, appels = un_client(ADRESSE_BLOQUEE)

    reponse = client.request(methode, "/api/ressource")

    assert reponse.status_code == HTTPStatus.FORBIDDEN
    assert reponse.headers["content-type"] == "application/problem+json"
    assert reponse.json()["detail"] == MESSAGE_NEUTRE
    assert appels == []


@pytest.mark.parametrize("chemin", ["/api/ressource", "/api/health"])
def test_une_adresse_bloquee_peut_encore_lire(chemin: str) -> None:
    client, _ = un_client(ADRESSE_BLOQUEE)

    reponse = client.get(chemin)

    assert reponse.status_code == HTTPStatus.OK


def test_une_autre_adresse_peut_ecrire() -> None:
    client, _ = un_client(ADRESSE_LIBRE)

    reponse = client.post("/api/ressource")

    assert reponse.status_code == HTTPStatus.OK


def test_une_ecriture_hors_de_l_api_n_est_pas_concernee() -> None:
    client, _ = un_client(ADRESSE_BLOQUEE)

    reponse = client.post("/hors-api")

    assert reponse.status_code == HTTPStatus.METHOD_NOT_ALLOWED
