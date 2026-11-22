"""Routes des étapes : parcours complet, droits, 404, 409 et 422."""

from http import HTTPStatus
from uuid import UUID

import pytest
from fastapi.testclient import TestClient

from tests.integration.conftest import CHEF, OUVRIER
from tests.integration.etapes.scenario import ajouter_etape, creer_chantier, transitionner

UUID_VERSION_7 = 7
VERSION_APRES_SIX_TRANSITIONS = 6
AVANCEMENT_COMPLET = 100
AVANCEMENT_MOITIE = 50


def avancement(client: TestClient, chantier_id: str) -> int:
    reponse = client.get(f"/api/chantiers/{chantier_id}", headers=CHEF)
    return int(reponse.json()["avancement"])


def test_une_etape_ajoutee_est_a_faire_et_propose_demarrer(client: TestClient) -> None:
    chantier_id = creer_chantier(client)

    reponse = client.post(
        f"/api/chantiers/{chantier_id}/etapes", json={"titre": "Gros œuvre"}, headers=CHEF
    )

    etape = reponse.json()
    assert reponse.status_code == HTTPStatus.CREATED
    assert UUID(etape.pop("id")).version == UUID_VERSION_7
    assert etape == {
        "chantier_id": chantier_id,
        "titre": "Gros œuvre",
        "ordre": 1,
        "statut": "a_faire",
        "version": 1,
        "actions_permises": ["demarrer"],
    }


def test_les_etapes_sont_listees_dans_leur_ordre(client: TestClient) -> None:
    chantier_id = creer_chantier(client)
    ajouter_etape(client, chantier_id, "Premier")
    ajouter_etape(client, chantier_id, "Second")

    reponse = client.get(f"/api/chantiers/{chantier_id}/etapes", headers=OUVRIER)

    assert [(e["titre"], e["ordre"]) for e in reponse.json()] == [("Premier", 1), ("Second", 2)]


def test_parcours_complet_de_la_creation_a_100_pour_cent(client: TestClient) -> None:
    chantier_id = creer_chantier(client)
    etape_id = ajouter_etape(client, chantier_id)

    demarree = transitionner(client, etape_id, "demarrer", OUVRIER)
    signalee = transitionner(client, etape_id, "signaler_terminee", OUVRIER)
    validation_ouvrier = transitionner(client, etape_id, "valider", OUVRIER)
    refus_sans_commentaire = transitionner(client, etape_id, "refuser", CHEF)
    refus = transitionner(client, etape_id, "refuser", CHEF, "Joints à reprendre")
    reprise = transitionner(client, etape_id, "signaler_terminee", OUVRIER)
    avancement_avant_validation = avancement(client, chantier_id)
    validee = transitionner(client, etape_id, "valider", CHEF)

    assert demarree.json()["statut"] == "en_cours"
    assert signalee.json()["statut"] == "terminee_a_valider"
    assert signalee.json()["actions_permises"] == []
    assert validation_ouvrier.status_code == HTTPStatus.CONFLICT
    assert refus_sans_commentaire.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert refus.json()["statut"] == "en_cours"
    assert reprise.json()["statut"] == "terminee_a_valider"
    assert avancement_avant_validation == 0
    assert validee.json()["statut"] == "validee"
    assert validee.json()["version"] == VERSION_APRES_SIX_TRANSITIONS
    assert avancement(client, chantier_id) == AVANCEMENT_COMPLET


def test_le_chef_voit_les_actions_de_validation_d_une_etape_terminee(client: TestClient) -> None:
    chantier_id = creer_chantier(client)
    etape_id = ajouter_etape(client, chantier_id)
    transitionner(client, etape_id, "demarrer", OUVRIER)
    transitionner(client, etape_id, "signaler_terminee", OUVRIER)

    etapes = client.get(f"/api/chantiers/{chantier_id}/etapes", headers=CHEF).json()

    assert etapes[0]["actions_permises"] == ["valider", "refuser"]


def test_l_avancement_est_la_part_d_etapes_validees(client: TestClient) -> None:
    chantier_id = creer_chantier(client)
    premiere, _ = ajouter_etape(client, chantier_id), ajouter_etape(client, chantier_id)
    for action, profil in (
        ("demarrer", OUVRIER),
        ("signaler_terminee", OUVRIER),
        ("valider", CHEF),
    ):
        transitionner(client, premiere, action, profil)

    liste = client.get("/api/chantiers", headers=CHEF).json()

    assert liste[0]["avancement"] == AVANCEMENT_MOITIE


def test_un_ouvrier_ne_peut_pas_ajouter_d_etape(client: TestClient) -> None:
    chantier_id = creer_chantier(client)

    reponse = client.post(
        f"/api/chantiers/{chantier_id}/etapes", json={"titre": "Gros œuvre"}, headers=OUVRIER
    )

    assert reponse.status_code == HTTPStatus.FORBIDDEN


def test_un_titre_vide_est_refuse_avec_un_422(client: TestClient) -> None:
    chantier_id = creer_chantier(client)

    reponse = client.post(
        f"/api/chantiers/{chantier_id}/etapes", json={"titre": "   "}, headers=CHEF
    )

    assert reponse.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_les_etapes_d_un_chantier_inexistant_donnent_un_404(client: TestClient) -> None:
    inconnu = UUID(int=1)

    liste = client.get(f"/api/chantiers/{inconnu}/etapes", headers=CHEF)
    ajout = client.post(f"/api/chantiers/{inconnu}/etapes", json={"titre": "x"}, headers=CHEF)

    assert (liste.status_code, ajout.status_code) == (HTTPStatus.NOT_FOUND, HTTPStatus.NOT_FOUND)


def test_une_transition_sur_une_etape_inexistante_donne_un_404(client: TestClient) -> None:
    reponse = transitionner(client, str(UUID(int=1)), "demarrer", CHEF)

    assert reponse.status_code == HTTPStatus.NOT_FOUND


def test_une_transition_hors_du_cycle_donne_un_409(client: TestClient) -> None:
    etape_id = ajouter_etape(client, creer_chantier(client))

    reponse = transitionner(client, etape_id, "valider", CHEF)

    assert reponse.status_code == HTTPStatus.CONFLICT
    assert reponse.headers["content-type"] == "application/problem+json"


def test_une_action_inconnue_donne_un_422(client: TestClient) -> None:
    etape_id = ajouter_etape(client, creer_chantier(client))

    reponse = transitionner(client, etape_id, "detruire", CHEF)

    assert reponse.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


@pytest.mark.parametrize(
    ("methode", "chemin"),
    [
        ("get", f"/api/chantiers/{UUID(int=1)}/etapes"),
        ("post", f"/api/chantiers/{UUID(int=1)}/etapes"),
        ("post", f"/api/etapes/{UUID(int=1)}/transitions"),
    ],
)
def test_sans_profil_les_routes_des_etapes_donnent_un_400(
    client: TestClient, methode: str, chemin: str
) -> None:
    reponse = client.request(methode, chemin, json={"titre": "x", "action": "demarrer"})

    assert reponse.status_code == HTTPStatus.BAD_REQUEST
