"""Erreurs de l'application complète : 404 de route, identifiants mal formés, 422 par champ, 503."""

import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from http import HTTPStatus
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.main import creer_application
from app.shared.infrastructure.sql.moteur import creer_moteur
from tests.conftest import url_sqlite
from tests.integration.conftest import CHANTIER_A_CREER, CHEF, parametres_de_test

TYPE_PROBLEME = "application/problem+json"
LONGUEUR_CODE_POSTAL_MAX = 10


def test_une_route_inconnue_de_l_api_donne_un_404_au_format_rfc_9457(client: TestClient) -> None:
    reponse = client.get("/api/nulle-part", headers=CHEF)

    assert reponse.status_code == HTTPStatus.NOT_FOUND
    assert reponse.headers["content-type"] == TYPE_PROBLEME
    assert reponse.json()["title"] == "Ressource introuvable"


def test_une_methode_non_permise_donne_un_405_au_format_rfc_9457(client: TestClient) -> None:
    reponse = client.delete("/api/chantiers", headers=CHEF)

    assert reponse.status_code == HTTPStatus.METHOD_NOT_ALLOWED
    assert reponse.headers["content-type"] == TYPE_PROBLEME
    assert "POST" in reponse.headers["allow"]


@pytest.mark.parametrize(
    ("methode", "chemin"),
    [
        ("get", "/api/chantiers/abc"),
        ("get", "/api/chantiers/abc/etapes"),
        ("post", "/api/etapes/abc/transitions"),
    ],
)
def test_un_identifiant_mal_forme_donne_un_404_comme_un_identifiant_inconnu(
    client: TestClient, methode: str, chemin: str
) -> None:
    corps = {"titre": "x", "action": "demarrer"}

    reponse = client.request(methode, chemin, json=corps, headers=CHEF)

    assert reponse.status_code == HTTPStatus.NOT_FOUND
    assert reponse.headers["content-type"] == TYPE_PROBLEME
    assert reponse.json()["detail"] == "Cette ressource n'existe pas."


def creer(client: TestClient, corps: dict[str, Any]) -> Any:
    return client.post("/api/chantiers", json=corps, headers=CHEF)


@pytest.mark.parametrize(
    ("modification", "champ", "message"),
    [
        ({"nom": ""}, "nom", "Le nom du chantier est obligatoire."),
        ({"nom": "n" * 201}, "nom", "Ce champ ne doit pas dépasser 200 caractères."),
        ({"client": "  "}, "client", "Le client du chantier est obligatoire."),
        (
            {"echeance": "2026-11-30"},
            "echeance",
            "L'échéance ne peut pas précéder la date de début.",
        ),
        ({"budget": "-5"}, "budget", "Le montant ne peut pas être négatif."),
        ({"budget": "abc"}, "budget", "Ce champ doit être un montant valide."),
        ({"budget": "1" * 13}, "budget", "Ce montant a trop de chiffres."),
        ({"budget": "99999999999"}, "budget", "Ce montant est trop élevé."),
        ({"budget": "1.234"}, "budget", "Ce montant ne doit pas avoir plus de 2 décimales."),
        ({"date_debut": "demain"}, "date_debut", "Ce champ doit être une date valide."),
    ],
)
def test_une_creation_invalide_designe_le_champ_fautif(
    client: TestClient, modification: dict[str, str], champ: str, message: str
) -> None:
    reponse = creer(client, {**CHANTIER_A_CREER, **modification})

    assert reponse.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert reponse.json()["erreurs"] == [{"champ": champ, "message": message}]


@pytest.mark.parametrize(
    ("adresse", "champ", "message"),
    [
        ({"voie": " "}, "adresse.voie", "La voie est obligatoire."),
        ({"ville": ""}, "adresse.ville", "La ville est obligatoire."),
        (
            {"code_postal": "1" * (LONGUEUR_CODE_POSTAL_MAX + 1)},
            "adresse.code_postal",
            "Ce champ ne doit pas dépasser 10 caractères.",
        ),
    ],
)
def test_une_adresse_invalide_est_designee_par_son_chemin_complet(
    client: TestClient, adresse: dict[str, str], champ: str, message: str
) -> None:
    corps = {**CHANTIER_A_CREER, "adresse": {**CHANTIER_A_CREER["adresse"], **adresse}}

    reponse = creer(client, corps)

    assert reponse.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert reponse.json()["erreurs"] == [{"champ": champ, "message": message}]


@contextmanager
def base_verrouillee(fichier: Path) -> Iterator[None]:
    """Garde la base verrouillée en écriture exclusive, comme le ferait un autre processus."""
    verrou = sqlite3.connect(fichier, isolation_level=None)
    verrou.execute("BEGIN EXCLUSIVE")
    try:
        yield
    finally:
        verrou.close()


def test_une_base_verrouillee_donne_un_503_generique(tmp_path: Path) -> None:
    # `timeout=0` : la requête échoue tout de suite au lieu d'attendre le verrou plusieurs secondes.
    parametres = parametres_de_test(tmp_path, url_base=f"{url_sqlite(tmp_path)}?timeout=0")

    with (
        TestClient(creer_application(parametres)) as client,
        base_verrouillee(tmp_path / "test.db"),
    ):
        reponse = client.get("/api/chantiers", headers=CHEF)

    assert reponse.status_code == HTTPStatus.SERVICE_UNAVAILABLE
    assert reponse.headers["content-type"] == TYPE_PROBLEME
    assert "chantiers" not in reponse.text
    assert reponse.json()["detail"] == (
        "Le service est momentanément indisponible : réessaie dans un instant."
    )


def supprimer_les_tables(dossier: Path) -> None:
    """Vide la base de son schéma, comme un déploiement dont la migration aurait échoué."""
    moteur = creer_moteur(url_sqlite(dossier))
    with moteur.begin() as connexion:
        for table in ("historique_etapes", "etapes", "chantiers"):
            connexion.execute(text(f"DROP TABLE {table}"))
    moteur.dispose()


def test_une_table_absente_donne_un_500_et_non_un_503(tmp_path: Path) -> None:
    # Un schéma incomplet est un défaut du programme ou du déploiement : le présenter comme une
    # panne passagère inviterait à réessayer sans fin, et cacherait la vraie cause au serveur.
    application = creer_application(parametres_de_test(tmp_path))
    with TestClient(application, raise_server_exceptions=False) as client:
        supprimer_les_tables(tmp_path)

        reponse = client.get("/api/chantiers", headers=CHEF)

    assert reponse.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
    assert reponse.headers["content-type"] == TYPE_PROBLEME
    assert "chantiers" not in reponse.text
    assert reponse.json()["detail"] == "Une erreur interne est survenue."
