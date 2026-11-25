"""Fausses adresses pièges : un 404 ordinaire, et l'adresse qui les touche est bloquée."""

from datetime import UTC, datetime, timedelta
from http import HTTPStatus

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.shared.api.blocage_ecritures import MiddlewareBlocageEcritures
from app.shared.api.erreurs import enregistrer_gestionnaires_erreurs
from app.shared.api.pieges import CHEMINS_PIEGES, creer_routeur_pieges
from app.shared.infrastructure.adresses_bloquees_memoire import MemoireListeAdressesBloquees
from app.shared.infrastructure.memoire.horloge_avancable import HorlogeAvancable

ADRESSE = "198.51.100.7"
CHEMINS_ATTENDUS = {
    "/wp-admin",
    "/wp-login.php",
    "/.env",
    "/.git",
    "/phpmyadmin",
    "/xmlrpc.php",
}


def une_application() -> tuple[TestClient, MemoireListeAdressesBloquees]:
    horloge = HorlogeAvancable(datetime(2026, 11, 24, 9, 0, tzinfo=UTC))
    liste = MemoireListeAdressesBloquees(horloge, timedelta(hours=1))
    application = FastAPI()
    enregistrer_gestionnaires_erreurs(application)
    application.include_router(creer_routeur_pieges(liste))
    return TestClient(application, client=(ADRESSE, 5000)), liste


def test_les_chemins_pieges_sont_ceux_de_la_liste_nommee() -> None:
    assert set(CHEMINS_PIEGES) == CHEMINS_ATTENDUS


@pytest.mark.parametrize("chemin", [*sorted(CHEMINS_ATTENDUS), "/wp-admin/install.php"])
def test_un_piege_repond_comme_une_adresse_inconnue_et_bloque_l_adresse(chemin: str) -> None:
    client, liste = une_application()
    inconnue = client.get("/rien-du-tout")

    reponse = client.get(chemin)

    assert reponse.status_code == HTTPStatus.NOT_FOUND
    assert reponse.json() == inconnue.json()
    assert reponse.headers["content-type"] == inconnue.headers["content-type"]
    assert liste.est_bloquee(ADRESSE)


@pytest.mark.parametrize("chemin", ["/.git/HEAD", "/.git/objects/ab/cdef", "/.git/"])
def test_tout_chemin_sous_git_est_un_piege(chemin: str) -> None:
    client, liste = une_application()
    inconnue = client.get("/rien-du-tout")

    reponse = client.get(chemin)

    assert reponse.status_code == HTTPStatus.NOT_FOUND
    assert reponse.json() == inconnue.json()
    assert liste.est_bloquee(ADRESSE)


@pytest.mark.parametrize("origine", ["same-origin", "same-site", "cross-site", "none"])
def test_un_piege_touche_par_un_navigateur_repond_404_sans_bloquer(origine: str) -> None:
    client, liste = une_application()
    inconnue = client.get("/rien-du-tout")

    reponse = client.get("/wp-admin", headers={"Sec-Fetch-Site": origine})

    assert reponse.status_code == HTTPStatus.NOT_FOUND
    assert reponse.json() == inconnue.json()
    assert not liste.est_bloquee(ADRESSE)


def test_un_piege_touche_en_ecriture_bloque_aussi_l_adresse() -> None:
    client, liste = une_application()

    reponse = client.post("/xmlrpc.php", json={})

    assert reponse.status_code == HTTPStatus.NOT_FOUND
    assert liste.est_bloquee(ADRESSE)


def test_une_adresse_inconnue_ne_bloque_pas() -> None:
    client, liste = une_application()

    client.get("/rien-du-tout")

    assert not liste.est_bloquee(ADRESSE)


def test_les_pieges_sont_absents_du_schema_openapi() -> None:
    client, _ = une_application()

    assert client.get("/openapi.json").json()["paths"] == {}


@pytest.mark.parametrize(
    "chemin",
    [
        "/WP-ADMIN",
        "/Wp-Login.PHP",
        "/.ENV",
        "/.GIT/config",
        "/.Git/HEAD",
        "/PhpMyAdmin/index.php",
        "/XMLRPC.php",
    ],
)
def test_un_piege_en_majuscules_repond_comme_une_adresse_inconnue_et_bloque(chemin: str) -> None:
    client, liste = une_application()
    inconnue = client.get("/rien-du-tout")

    reponse = client.get(chemin)

    assert reponse.status_code == HTTPStatus.NOT_FOUND
    assert reponse.json() == inconnue.json()
    assert liste.est_bloquee(ADRESSE)


def test_un_piege_touche_par_une_adresse_deja_bloquee_garde_la_reponse_d_une_adresse_inconnue() -> (
    None
):
    client, liste = une_application()
    liste.bloquer(ADRESSE)
    application = client.app
    assert isinstance(application, FastAPI)
    application.add_middleware(MiddlewareBlocageEcritures, liste=liste)
    inconnue = client.post("/rien-du-tout")

    reponse = client.post("/wp-admin", json={})

    assert reponse.status_code == HTTPStatus.NOT_FOUND
    assert reponse.json() == inconnue.json()
