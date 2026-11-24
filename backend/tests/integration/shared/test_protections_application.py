"""Protections branchées sur l'application réelle : débit, pièges et champ piège.

Chaque middleware et chaque garde est déjà testé seul. Ces tests prouvent que la composition
les relie bien, à la même liste d'adresses bloquées et au même limiteur, avec les seuils
décidés par le propriétaire (`client_protege` n'en change aucun).
"""

from http import HTTPStatus
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import creer_application
from app.shared.api.champ_piege import NOM_CHAMP_PIEGE
from app.shared.application.limites_debit import ECRITURES_PAR_FENETRE, LECTURES_PAR_FENETRE
from tests.integration.conftest import CHANTIER_A_CREER, CHEF, parametres_de_test
from tests.integration.etapes.scenario import creer_chantier

DELAI_MAXIMAL = 60


def test_la_vingt_et_unieme_ecriture_de_la_minute_est_refusee_en_429(
    client_protege: TestClient,
) -> None:
    for _ in range(ECRITURES_PAR_FENETRE):
        permise = client_protege.post("/api/chantiers", json=CHANTIER_A_CREER, headers=CHEF)
        assert permise.status_code == HTTPStatus.CREATED

    reponse = client_protege.post("/api/chantiers", json=CHANTIER_A_CREER, headers=CHEF)

    assert reponse.status_code == HTTPStatus.TOO_MANY_REQUESTS
    assert 1 <= int(reponse.headers["retry-after"]) <= DELAI_MAXIMAL
    assert reponse.headers["content-type"] == "application/problem+json"


def test_le_quota_d_ecritures_n_empeche_pas_de_lire(client_protege: TestClient) -> None:
    for _ in range(ECRITURES_PAR_FENETRE + 1):
        client_protege.post("/api/chantiers", json=CHANTIER_A_CREER, headers=CHEF)

    reponse = client_protege.get("/api/chantiers", headers=CHEF)

    assert reponse.status_code == HTTPStatus.OK


def test_la_sonde_de_sante_n_est_jamais_limitee(client_protege: TestClient) -> None:
    statuts = {
        client_protege.get("/api/health").status_code for _ in range(LECTURES_PAR_FENETRE + 1)
    }

    assert statuts == {HTTPStatus.OK}
    assert client_protege.get("/api/chantiers", headers=CHEF).status_code == HTTPStatus.OK


def test_apres_un_piege_les_ecritures_sont_refusees_mais_les_lectures_passent(
    client_protege: TestClient,
) -> None:
    piege = client_protege.get("/wp-admin")

    ecriture = client_protege.post("/api/chantiers", json=CHANTIER_A_CREER, headers=CHEF)
    lecture = client_protege.get("/api/chantiers", headers=CHEF)

    assert piege.status_code == HTTPStatus.NOT_FOUND
    assert ecriture.status_code == HTTPStatus.FORBIDDEN
    assert lecture.status_code == HTTPStatus.OK


def test_le_champ_piege_rempli_refuse_l_ecriture_et_ne_cree_rien(
    client_protege: TestClient,
) -> None:
    reponse = client_protege.post(
        "/api/chantiers", json={**CHANTIER_A_CREER, NOM_CHAMP_PIEGE: "robot"}, headers=CHEF
    )

    assert reponse.status_code == HTTPStatus.FORBIDDEN
    assert client_protege.get("/api/chantiers", headers=CHEF).json() == []


def test_le_champ_piege_bloque_aussi_les_ecritures_suivantes(client_protege: TestClient) -> None:
    client_protege.post(
        "/api/chantiers", json={**CHANTIER_A_CREER, NOM_CHAMP_PIEGE: "robot"}, headers=CHEF
    )

    reponse = client_protege.post("/api/chantiers", json=CHANTIER_A_CREER, headers=CHEF)

    assert reponse.status_code == HTTPStatus.FORBIDDEN


def test_les_seuils_du_limiteur_viennent_des_parametres(tmp_path: Path) -> None:
    parametres = parametres_de_test(tmp_path, ecritures_par_minute=2)

    with TestClient(creer_application(parametres)) as client:
        statuts = [
            client.post("/api/chantiers", json=CHANTIER_A_CREER, headers=CHEF).status_code
            for _ in range(3)
        ]

    assert statuts == [HTTPStatus.CREATED, HTTPStatus.CREATED, HTTPStatus.TOO_MANY_REQUESTS]


def test_une_etape_avec_le_champ_piege_rempli_n_est_pas_creee(client_protege: TestClient) -> None:
    chantier_id = creer_chantier(client_protege)

    reponse = client_protege.post(
        f"/api/chantiers/{chantier_id}/etapes",
        json={"titre": "Gros œuvre", NOM_CHAMP_PIEGE: "robot"},
        headers=CHEF,
    )

    assert reponse.status_code == HTTPStatus.FORBIDDEN
    assert client_protege.get(f"/api/chantiers/{chantier_id}/etapes", headers=CHEF).json() == []


def test_un_champ_piege_vide_est_accepte_et_ne_bloque_personne(client_protege: TestClient) -> None:
    reponse = client_protege.post(
        "/api/chantiers", json={**CHANTIER_A_CREER, NOM_CHAMP_PIEGE: ""}, headers=CHEF
    )
    suivante = client_protege.post("/api/chantiers", json=CHANTIER_A_CREER, headers=CHEF)

    assert reponse.status_code == HTTPStatus.CREATED
    assert NOM_CHAMP_PIEGE not in reponse.json()
    assert suivante.status_code == HTTPStatus.CREATED
