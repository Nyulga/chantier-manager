"""Schéma OpenAPI : les corps d'erreur sont typés, pour que le client généré les connaisse."""

from typing import Any

import pytest
from fastapi.testclient import TestClient

STATUT_D_ERREUR_MINIMAL = 400
PREFIXE_SCHEMA = "#/components/schemas/"
PROBLEME = PREFIXE_SCHEMA + "ProblemeReponse"
PROBLEME_DE_VALIDATION = PREFIXE_SCHEMA + "ProblemeValidationReponse"


def schema_openapi(client: TestClient) -> dict[str, Any]:
    schema: dict[str, Any] = client.get("/api/openapi.json").json()
    return schema


def reponses_declarees(schema: dict[str, Any]) -> list[tuple[str, str, str, dict[str, Any]]]:
    """Liste toutes les réponses déclarées : (chemin, méthode, statut, réponse)."""
    return [
        (chemin, methode, statut, reponse)
        for chemin, operations in schema["paths"].items()
        for methode, operation in operations.items()
        for statut, reponse in operation["responses"].items()
    ]


def schemas_des_erreurs(schema: dict[str, Any]) -> dict[tuple[str, str, str], str]:
    """Associe chaque réponse d'erreur (chemin, méthode, statut) au schéma de son corps."""
    return {
        (chemin, methode, statut): reponse.get("content", {})
        .get("application/json", {})
        .get("schema", {})
        .get("$ref", "")
        for chemin, methode, statut, reponse in reponses_declarees(schema)
        if int(statut) >= STATUT_D_ERREUR_MINIMAL
    }


def test_chaque_reponse_d_erreur_a_un_corps_type_en_rfc_9457(client: TestClient) -> None:
    erreurs = schemas_des_erreurs(schema_openapi(client))

    assert erreurs
    assert set(erreurs.values()) <= {PROBLEME, PROBLEME_DE_VALIDATION}


def test_les_422_declarent_la_liste_des_erreurs_par_champ(client: TestClient) -> None:
    erreurs = schemas_des_erreurs(schema_openapi(client))

    assert {schema for (_, _, statut), schema in erreurs.items() if statut == "422"} == {
        PROBLEME_DE_VALIDATION
    }


def test_le_probleme_de_validation_ajoute_la_liste_des_erreurs_au_probleme(
    client: TestClient,
) -> None:
    schemas = schema_openapi(client)["components"]["schemas"]

    assert set(schemas["ProblemeReponse"]["properties"]) == {"type", "title", "status", "detail"}
    assert set(schemas["ProblemeValidationReponse"]["properties"]) == {
        "type",
        "title",
        "status",
        "detail",
        "erreurs",
    }
    assert set(schemas["ErreurChampReponse"]["properties"]) == {"champ", "message"}


@pytest.mark.parametrize(
    ("chemin", "statuts"),
    [
        ("/api/chantiers", {"400", "403", "409", "422", "503"}),
        ("/api/chantiers/{chantier_id}/etapes", {"400", "403", "404", "409", "422", "503"}),
        ("/api/chantiers/{chantier_id}", {"400", "404", "503"}),
        ("/api/etapes/{etape_id}/transitions", {"400", "403", "404", "409", "422", "503"}),
        ("/api/moi", {"400", "503"}),
    ],
)
def test_les_erreurs_possibles_de_chaque_route_sont_documentees(
    client: TestClient, chemin: str, statuts: set[str]
) -> None:
    operations = schema_openapi(client)["paths"][chemin]
    documentes = {statut for operation in operations.values() for statut in operation["responses"]}

    assert statuts <= documentes
