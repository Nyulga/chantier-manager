"""Les protections comptent par abonné, pas par adresse : un /64 IPv6 vaut une seule clé.

Un abonné IPv6 reçoit au moins un bloc /64 (2^64 adresses) : sans regroupement, un robot
qui change d'adresse à chaque requête ne serait jamais limité ni bloqué (ADR 0016).
Les tests passent par l'application réelle, avec une adresse de client choisie.
"""

from collections.abc import Iterator
from http import HTTPStatus
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.main import creer_application
from app.shared.api.acces_http import ADRESSE_INCONNUE, cle_du_client
from app.shared.api.champ_piege import NOM_CHAMP_PIEGE
from app.shared.application.limites_debit import ECRITURES_PAR_FENETRE
from tests.integration.conftest import CHANTIER_A_CREER, CHEF, parametres_de_test

# Plages réservées à la documentation (RFC 3849 et RFC 5737) : aucune adresse réelle.
V6_A = "2001:db8:0:1::1"
V6_MEME_BLOC = "2001:db8:0:1:ffff::2"
V6_AUTRE_BLOC = "2001:db8:0:2::1"
V4 = "192.0.2.10"
V4_VOISINE = "192.0.2.11"
V4_ENCAPSULEE = "::ffff:192.0.2.10"


@pytest.fixture
def application(tmp_path: Path) -> Iterator[FastAPI]:
    yield creer_application(parametres_de_test(tmp_path))


def _client(application: FastAPI, adresse: str) -> TestClient:
    return TestClient(application, client=(adresse, 5000))


def _ecrire(client: TestClient) -> int:
    reponse = client.post("/api/chantiers", json=CHANTIER_A_CREER, headers=CHEF)
    return int(reponse.status_code)


def _epuiser_le_quota(client: TestClient) -> None:
    for _ in range(ECRITURES_PAR_FENETRE):
        assert _ecrire(client) == HTTPStatus.CREATED


def test_deux_adresses_du_meme_bloc_partagent_la_limite_de_debit(application: FastAPI) -> None:
    with _client(application, V6_A) as premier, _client(application, V6_MEME_BLOC) as second:
        _epuiser_le_quota(premier)

        assert _ecrire(second) == HTTPStatus.TOO_MANY_REQUESTS


def test_deux_blocs_differents_ont_chacun_leur_limite(application: FastAPI) -> None:
    with _client(application, V6_A) as premier, _client(application, V6_AUTRE_BLOC) as second:
        _epuiser_le_quota(premier)

        assert _ecrire(second) == HTTPStatus.CREATED


def test_un_piege_touche_bloque_tout_le_bloc_en_ecriture(application: FastAPI) -> None:
    with _client(application, V6_A) as robot, _client(application, V6_MEME_BLOC) as voisin:
        robot.get("/wp-admin")

        assert _ecrire(voisin) == HTTPStatus.FORBIDDEN


def test_un_piege_ne_bloque_pas_un_autre_bloc(application: FastAPI) -> None:
    with _client(application, V6_A) as robot, _client(application, V6_AUTRE_BLOC) as autre:
        robot.get("/wp-admin")

        assert _ecrire(autre) == HTTPStatus.CREATED


def test_le_champ_piege_bloque_tout_le_bloc(application: FastAPI) -> None:
    with _client(application, V6_A) as robot, _client(application, V6_MEME_BLOC) as voisin:
        robot.post("/api/chantiers", json={**CHANTIER_A_CREER, NOM_CHAMP_PIEGE: "x"}, headers=CHEF)

        assert _ecrire(voisin) == HTTPStatus.FORBIDDEN


def test_une_ipv4_reste_comptee_a_l_adresse_exacte(application: FastAPI) -> None:
    with _client(application, V4) as robot, _client(application, V4_VOISINE) as voisin:
        robot.get("/wp-admin")

        assert _ecrire(voisin) == HTTPStatus.CREATED


def test_une_ipv4_encapsulee_en_ipv6_compte_comme_l_ipv4(application: FastAPI) -> None:
    with _client(application, V4) as robot, _client(application, V4_ENCAPSULEE) as meme:
        robot.get("/wp-admin")

        assert _ecrire(meme) == HTTPStatus.FORBIDDEN


def test_une_valeur_illisible_est_gardee_telle_quelle_et_partagee(application: FastAPI) -> None:
    # Le client de test de Starlette donne le nom « testclient », qui n'est pas une adresse.
    with _client(application, "testclient") as robot, _client(application, "testclient") as autre:
        robot.get("/wp-admin")

        assert _ecrire(autre) == HTTPStatus.FORBIDDEN


def test_une_valeur_illisible_ne_bloque_pas_une_vraie_adresse(application: FastAPI) -> None:
    with _client(application, "testclient") as robot, _client(application, V4) as visiteur:
        robot.get("/wp-admin")

        assert _ecrire(visiteur) == HTTPStatus.CREATED


def test_sans_adresse_de_client_tous_les_acces_partagent_la_cle_inconnue() -> None:
    # Le client de test impose toujours une adresse : on lit donc la clé d'une portée sans client.
    assert cle_du_client({"client": None}) == ADRESSE_INCONNUE
    assert cle_du_client({}) == ADRESSE_INCONNUE
