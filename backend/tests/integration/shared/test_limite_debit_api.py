"""Middleware de limite de débit : 429 avec `Retry-After`, catégories, sonde de santé exemptée."""

from datetime import UTC, datetime, timedelta
from http import HTTPStatus

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.shared.api.limite_debit import MiddlewareLimiteDebit
from app.shared.api.pieges import creer_routeur_pieges
from app.shared.application.ports import CategorieAcces
from app.shared.infrastructure.adresses_bloquees_memoire import MemoireListeAdressesBloquees
from app.shared.infrastructure.limiteur_debit_memoire import MemoireLimiteurDebit
from app.shared.infrastructure.memoire.horloge_avancable import HorlogeAvancable
from tests.integration.shared.petite_application import une_petite_application

FENETRE = timedelta(seconds=60)
SEUIL_ECRITURES = 2
SEUIL_LECTURES = 3
MESSAGE = "Trop de demandes. Réessaie dans quelques instants."


SEUIL_ECRITURES_BLOC = 4
SEUIL_LECTURES_BLOC = 6
# Plage réservée à la documentation (RFC 3849) : un même /48, des /64 différents.
V6_BLOC_A = "2001:db8:1:1::1"
V6_BLOC_A_VOISIN = "2001:db8:1:1::2"


def un_limiteur(horloge: HorlogeAvancable, ecritures: int, lectures: int) -> MemoireLimiteurDebit:
    seuils = {CategorieAcces.ECRITURE: ecritures, CategorieAcces.LECTURE: lectures}
    return MemoireLimiteurDebit(horloge, seuils, FENETRE, cles_max=10)


def une_application_limitee() -> tuple[FastAPI, list[str], HorlogeAvancable]:
    """Petite application avec la route factice, les pièges et les deux limiteurs."""
    horloge = HorlogeAvancable(datetime(2026, 11, 24, 9, 0, tzinfo=UTC))
    application, appels = une_petite_application()
    liste = MemoireListeAdressesBloquees(horloge, timedelta(hours=1))
    application.include_router(creer_routeur_pieges(liste))
    application.add_middleware(
        MiddlewareLimiteDebit,
        limiteur=un_limiteur(horloge, SEUIL_ECRITURES, SEUIL_LECTURES),
        limiteur_bloc_48=un_limiteur(horloge, SEUIL_ECRITURES_BLOC, SEUIL_LECTURES_BLOC),
    )
    return application, appels, horloge


def un_client() -> tuple[TestClient, list[str], HorlogeAvancable]:
    application, appels, horloge = une_application_limitee()
    return TestClient(application), appels, horloge


def un_client_a(application: FastAPI, adresse: str) -> TestClient:
    return TestClient(application, client=(adresse, 5000))


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


def test_des_blocs_64_differents_d_un_meme_bloc_48_finissent_en_429() -> None:
    application, _, _ = une_application_limitee()
    adresses = [f"2001:db8:1:{n}::1" for n in range(1, SEUIL_ECRITURES_BLOC + 2)]

    statuts = [
        un_client_a(application, adresse).post("/api/ressource").status_code for adresse in adresses
    ]

    assert statuts == [HTTPStatus.OK] * SEUIL_ECRITURES_BLOC + [HTTPStatus.TOO_MANY_REQUESTS]


def test_une_adresse_au_dela_de_son_quota_n_entame_pas_le_quota_du_bloc_48() -> None:
    application, _, _ = une_application_limitee()
    insistante = un_client_a(application, V6_BLOC_A)
    for _ in range(SEUIL_ECRITURES + 5):
        insistante.post("/api/ressource")

    # Il reste au bloc SEUIL_ECRITURES_BLOC - SEUIL_ECRITURES accès : les refus de l'insistante
    # n'ont rien consommé, ses voisins du même /48 peuvent donc encore écrire.
    voisines = [f"2001:db8:1:{n}::1" for n in range(2, 2 + SEUIL_ECRITURES_BLOC - SEUIL_ECRITURES)]
    statuts = [
        un_client_a(application, adresse).post("/api/ressource").status_code for adresse in voisines
    ]

    assert statuts == [HTTPStatus.OK] * len(voisines)


def test_deux_adresses_du_meme_bloc_64_partagent_le_quota_habituel() -> None:
    application, _, _ = une_application_limitee()
    for _ in range(SEUIL_ECRITURES):
        un_client_a(application, V6_BLOC_A).post("/api/ressource")

    reponse = un_client_a(application, V6_BLOC_A_VOISIN).post("/api/ressource")

    assert reponse.status_code == HTTPStatus.TOO_MANY_REQUESTS


def test_une_ipv4_n_a_qu_une_cle_et_ne_consomme_pas_le_quota_des_blocs() -> None:
    application, _, _ = une_application_limitee()
    ipv4 = un_client_a(application, "192.0.2.10")
    for _ in range(SEUIL_ECRITURES):
        ipv4.post("/api/ressource")

    refusee = ipv4.post("/api/ressource")
    ipv6 = un_client_a(application, V6_BLOC_A).post("/api/ressource")

    assert refusee.status_code == HTTPStatus.TOO_MANY_REQUESTS
    assert ipv6.status_code == HTTPStatus.OK


@pytest.mark.parametrize("variante", ["/wp-admin", "/WP-ADMIN", "/.GIT/config", "/Wp-Login.PHP"])
def test_un_chemin_piege_est_limite_en_debit_meme_en_majuscules(variante: str) -> None:
    client, _, _ = un_client()
    for _ in range(SEUIL_LECTURES):
        assert client.get("/wp-admin").status_code == HTTPStatus.NOT_FOUND

    reponse = client.get(variante)

    assert reponse.status_code == HTTPStatus.TOO_MANY_REQUESTS
    assert reponse.headers["retry-after"] == "60"


def test_une_ecriture_sur_un_piege_compte_comme_une_ecriture() -> None:
    client, _, _ = un_client()
    for _ in range(SEUIL_ECRITURES):
        client.post("/xmlrpc.php", json={})

    reponse = client.post("/api/ressource")

    assert reponse.status_code == HTTPStatus.TOO_MANY_REQUESTS
