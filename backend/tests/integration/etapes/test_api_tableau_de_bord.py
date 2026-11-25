"""Routes du tableau de bord : étapes à valider, activité récente, compteurs et délai."""

from collections.abc import Callable
from http import HTTPStatus
from typing import Any

import pytest
from fastapi.testclient import TestClient

from tests.integration.conftest import CHANTIER_A_CREER, CHEF, OUVRIER
from tests.integration.etapes.scenario import (
    ajouter_etape,
    creer_chantier,
    signaler_terminee,
    transitionner,
)

LIMITE_PAR_DEFAUT = 10
# Le plafond de la liste « À valider » fixé par la couche application (`LIMITE_A_VALIDER`).
LIMITE_A_VALIDER = 50
# Le plafond d'étapes par chantier de la démo (`LIMITE_ETAPES_PAR_CHANTIER`).
ETAPES_PAR_CHANTIER = 30
VERSION_APRES_SIGNALEMENT = 3
ETAPES_POUR_DEPASSER_LA_LIMITE = 6
ECHEANCE_LOINTAINE = {**CHANTIER_A_CREER, "echeance": "2999-12-31"}
ECHEANCE_DEPASSEE = {**CHANTIER_A_CREER, "date_debut": "2020-01-01", "echeance": "2020-01-31"}


def a_valider(client: TestClient) -> list[dict[str, Any]]:
    reponse = client.get("/api/etapes/a-valider", headers=CHEF)
    assert reponse.status_code == HTTPStatus.OK
    liste: list[dict[str, Any]] = reponse.json()
    return liste


def activite(client: TestClient, parametres: dict[str, int] | None = None) -> list[dict[str, Any]]:
    reponse = client.get("/api/activite", params=parametres, headers=OUVRIER)
    assert reponse.status_code == HTTPStatus.OK
    liste: list[dict[str, Any]] = reponse.json()
    return liste


def etapes_signalees_dans_l_ordre(client: TestClient, nombre: int) -> list[str]:
    """Crée `nombre` étapes, et les signale terminées dans l'ordre de création.

    Un chantier ne peut pas avoir plus de `ETAPES_PAR_CHANTIER` étapes : les étapes sont
    donc réparties sur autant de chantiers qu'il en faut, créés au fur et à mesure.
    """
    chantiers = [creer_chantier(client) for _ in range(0, nombre, ETAPES_PAR_CHANTIER)]
    etapes = [
        ajouter_etape(client, chantiers[rang // ETAPES_PAR_CHANTIER]) for rang in range(nombre)
    ]
    for etape_id in etapes:
        signaler_terminee(client, etape_id)
    return etapes


def signaler_des_etapes_pour_depasser_la_limite(client: TestClient) -> None:
    """Crée assez d'étapes signalées terminées pour que le fil d'activité dépasse sa limite."""
    chantier_id = creer_chantier(client)
    etapes = [ajouter_etape(client, chantier_id) for _ in range(ETAPES_POUR_DEPASSER_LA_LIMITE)]
    for etape_id in etapes:
        signaler_terminee(client, etape_id)


def test_sans_etape_signalee_la_liste_a_valider_est_vide(client: TestClient) -> None:
    creer_chantier(client)

    reponse = client.get("/api/etapes/a-valider", headers=CHEF)

    assert (reponse.status_code, reponse.json()) == (HTTPStatus.OK, [])


def test_une_etape_signalee_apparait_a_valider_puis_disparait_une_fois_validee(
    client: TestClient,
) -> None:
    chantier_id = creer_chantier(client)
    etape_id = ajouter_etape(client, chantier_id, "Plomberie")
    transitionner(client, etape_id, "demarrer", OUVRIER)
    avant_signalement = a_valider(client)
    transitionner(client, etape_id, "signaler_terminee", OUVRIER)

    en_attente = a_valider(client)
    transitionner(client, etape_id, "valider", CHEF)
    apres_validation = a_valider(client)

    assert avant_signalement == []
    assert [(e["id"], e["chantier_id"], e["titre"]) for e in en_attente] == [
        (etape_id, chantier_id, "Plomberie")
    ]
    assert en_attente[0]["actions_permises"] == ["valider", "refuser"]
    assert en_attente[0]["version"] == VERSION_APRES_SIGNALEMENT
    assert en_attente[0]["signalee_le"] is not None
    assert apres_validation == []


def test_les_etapes_a_valider_vont_de_la_plus_anciennement_signalee_a_la_plus_recente(
    client: TestClient,
) -> None:
    chantier_id = creer_chantier(client)
    premiere = ajouter_etape(client, chantier_id, "Première")
    seconde = ajouter_etape(client, chantier_id, "Seconde")
    signaler_terminee(client, seconde)
    signaler_terminee(client, premiere)

    titres = [etape["titre"] for etape in a_valider(client)]

    assert titres == ["Seconde", "Première"]


def test_la_liste_a_valider_est_plafonnee_et_garde_les_plus_anciennes(
    client: TestClient,
) -> None:
    etapes = etapes_signalees_dans_l_ordre(client, LIMITE_A_VALIDER + 1)

    identifiants = [etape["id"] for etape in a_valider(client)]

    assert identifiants == etapes[:LIMITE_A_VALIDER]


def test_un_ouvrier_ne_peut_pas_lister_les_etapes_a_valider(client: TestClient) -> None:
    reponse = client.get("/api/etapes/a-valider", headers=OUVRIER)

    assert reponse.status_code == HTTPStatus.FORBIDDEN
    assert reponse.headers["content-type"] == "application/problem+json"


@pytest.mark.parametrize("chemin", ["/api/etapes/a-valider", "/api/activite"])
def test_sans_profil_les_routes_du_tableau_de_bord_donnent_un_400(
    client: TestClient, chemin: str
) -> None:
    reponse = client.get(chemin)

    assert reponse.status_code == HTTPStatus.BAD_REQUEST


def test_l_activite_va_de_la_transition_la_plus_recente_a_la_plus_ancienne(
    client: TestClient,
) -> None:
    etape_id = ajouter_etape(client, creer_chantier(client), "Peinture")
    signaler_terminee(client, etape_id)
    transitionner(client, etape_id, "refuser", CHEF, "Reprendre les angles")

    entrees = activite(client)

    assert [(e["role"], e["ancien_statut"], e["nouveau_statut"]) for e in entrees] == [
        ("chef", "terminee_a_valider", "en_cours"),
        ("ouvrier", "en_cours", "terminee_a_valider"),
        ("ouvrier", "a_faire", "en_cours"),
    ]
    assert entrees[0]["commentaire"] == "Reprendre les angles"
    assert entrees[1]["commentaire"] is None
    assert (entrees[0]["etape_id"], entrees[0]["titre_etape"]) == (etape_id, "Peinture")
    assert entrees[0]["date"] >= entrees[1]["date"] >= entrees[2]["date"]


def test_l_activite_est_vide_sans_transition(client: TestClient) -> None:
    ajouter_etape(client, creer_chantier(client))

    assert activite(client) == []


def test_la_limite_par_defaut_du_fil_d_activite_est_celle_du_domaine(client: TestClient) -> None:
    signaler_des_etapes_pour_depasser_la_limite(client)

    assert len(activite(client)) == LIMITE_PAR_DEFAUT


def test_la_limite_demandee_borne_le_fil_d_activite(client: TestClient) -> None:
    signaler_terminee(client, ajouter_etape(client, creer_chantier(client)))

    entrees = activite(client, {"limite": 1})

    assert [e["nouveau_statut"] for e in entrees] == ["terminee_a_valider"]


@pytest.mark.parametrize("limite", ["0", "51", "-1", "abc"])
def test_une_limite_hors_bornes_donne_un_422(client: TestClient, limite: str) -> None:
    reponse = client.get("/api/activite", params={"limite": limite}, headers=CHEF)

    assert reponse.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert reponse.headers["content-type"] == "application/problem+json"


def chantier_de_la_liste(client: TestClient, _chantier_id: str) -> Any:
    return client.get("/api/chantiers", headers=OUVRIER).json()[0]


def chantier_du_detail(client: TestClient, chantier_id: str) -> Any:
    return client.get(f"/api/chantiers/{chantier_id}", headers=CHEF).json()


@pytest.mark.parametrize("lire_chantier", [chantier_de_la_liste, chantier_du_detail])
def test_les_compteurs_d_etapes_sont_dans_la_liste_et_le_detail_des_chantiers(
    client: TestClient, lire_chantier: Callable[[TestClient, str], Any]
) -> None:
    chantier_id = creer_chantier(client)
    validee, signalee, _ = (ajouter_etape(client, chantier_id) for _ in range(3))
    signaler_terminee(client, validee)
    transitionner(client, validee, "valider", CHEF)
    signaler_terminee(client, signalee)

    chantier = lire_chantier(client, chantier_id)

    assert (chantier["etapes_validees"], chantier["etapes_total"]) == (1, 3)
    assert chantier["etapes_a_valider"] == 1


def test_un_chantier_sans_etape_a_des_compteurs_nuls(client: TestClient) -> None:
    creer_chantier(client)

    chantier = client.get("/api/chantiers", headers=CHEF).json()[0]

    assert (chantier["etapes_validees"], chantier["etapes_total"]) == (0, 0)
    assert chantier["etapes_a_valider"] == 0


def test_un_chantier_a_l_echeance_lointaine_a_des_jours_restants(client: TestClient) -> None:
    chantier_id = creer_chantier(client, ECHEANCE_LOINTAINE)

    chantier = client.get(f"/api/chantiers/{chantier_id}", headers=CHEF).json()

    assert chantier["en_retard"] is False
    assert chantier["jours_restants"] > 0


def test_un_chantier_a_l_echeance_depassee_est_en_retard_de_plusieurs_jours(
    client: TestClient,
) -> None:
    chantier_id = creer_chantier(client, ECHEANCE_DEPASSEE)

    chantier = client.get(f"/api/chantiers/{chantier_id}", headers=OUVRIER).json()

    assert chantier["en_retard"] is True
    assert chantier["jours_restants"] > 0


def test_une_liste_a_valider_complete_n_est_pas_signalee_tronquee(client: TestClient) -> None:
    etapes_signalees_dans_l_ordre(client, LIMITE_A_VALIDER)

    reponse = client.get("/api/etapes/a-valider", headers=CHEF)

    assert len(reponse.json()) == LIMITE_A_VALIDER
    assert reponse.headers["X-Liste-Tronquee"] == "false"


def test_une_liste_a_valider_coupee_au_plafond_est_signalee_tronquee(client: TestClient) -> None:
    etapes_signalees_dans_l_ordre(client, LIMITE_A_VALIDER + 1)

    reponse = client.get("/api/etapes/a-valider", headers=CHEF)

    assert len(reponse.json()) == LIMITE_A_VALIDER
    assert reponse.headers["X-Liste-Tronquee"] == "true"


def test_l_en_tete_de_troncature_est_documente_dans_openapi(client: TestClient) -> None:
    schema = client.get("/api/openapi.json").json()

    en_tetes = schema["paths"]["/api/etapes/a-valider"]["get"]["responses"]["200"]["headers"]

    assert en_tetes["X-Liste-Tronquee"]["schema"]["enum"] == ["true", "false"]
