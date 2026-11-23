"""Route `GET /api/moi` : les capacités de l'acteur, d'après son profil."""

from http import HTTPStatus

import pytest
from fastapi.testclient import TestClient

from tests.integration.conftest import CHEF, OUVRIER


@pytest.mark.parametrize(
    ("profil", "attendu"),
    [
        (
            CHEF,
            {"role": "chef", "peut_creer_chantier": True, "peut_lister_etapes_a_valider": True},
        ),
        (
            OUVRIER,
            {
                "role": "ouvrier",
                "peut_creer_chantier": False,
                "peut_lister_etapes_a_valider": False,
            },
        ),
    ],
    ids=["chef", "ouvrier"],
)
def test_les_capacites_sont_celles_des_politiques_du_profil(
    client: TestClient, profil: dict[str, str], attendu: dict[str, object]
) -> None:
    reponse = client.get("/api/moi", headers=profil)

    assert reponse.status_code == HTTPStatus.OK
    assert reponse.json() == attendu


@pytest.mark.parametrize("en_tetes", [{}, {"X-Profil": "directeur"}])
def test_sans_profil_valide_les_capacites_donnent_un_400(
    client: TestClient, en_tetes: dict[str, str]
) -> None:
    reponse = client.get("/api/moi", headers=en_tetes)

    assert reponse.status_code == HTTPStatus.BAD_REQUEST
    assert reponse.headers["content-type"] == "application/problem+json"
