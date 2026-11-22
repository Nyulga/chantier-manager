"""Étapes de scénario communes aux tests d'API des étapes : créer, ajouter, faire avancer."""

from http import HTTPStatus
from typing import Any

from fastapi.testclient import TestClient

from tests.integration.conftest import CHANTIER_A_CREER, CHEF, OUVRIER


def creer_chantier(client: TestClient, corps: dict[str, Any] | None = None) -> str:
    reponse = client.post("/api/chantiers", json=corps or CHANTIER_A_CREER, headers=CHEF)
    return str(reponse.json()["id"])


def ajouter_etape(client: TestClient, chantier_id: str, titre: str = "Gros œuvre") -> str:
    reponse = client.post(
        f"/api/chantiers/{chantier_id}/etapes", json={"titre": titre}, headers=CHEF
    )
    assert reponse.status_code == HTTPStatus.CREATED
    return str(reponse.json()["id"])


def transitionner(
    client: TestClient,
    etape_id: str,
    action: str,
    profil: dict[str, str],
    commentaire: str | None = None,
) -> Any:
    corps = {"action": action, "commentaire": commentaire}
    return client.post(f"/api/etapes/{etape_id}/transitions", json=corps, headers=profil)


def signaler_terminee(client: TestClient, etape_id: str) -> None:
    """Fait démarrer puis signaler terminée une étape, comme le ferait un ouvrier."""
    transitionner(client, etape_id, "demarrer", OUVRIER)
    transitionner(client, etape_id, "signaler_terminee", OUVRIER)
