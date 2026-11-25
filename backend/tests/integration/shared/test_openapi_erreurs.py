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
        ("/api/chantiers", {"400", "403", "409", "413", "422", "429", "503"}),
        (
            "/api/chantiers/{chantier_id}/etapes",
            {"400", "403", "404", "409", "413", "422", "429", "503"},
        ),
        ("/api/chantiers/{chantier_id}", {"400", "404", "429", "503"}),
        (
            "/api/etapes/{etape_id}/transitions",
            {"400", "403", "404", "409", "413", "422", "429", "503"},
        ),
        ("/api/moi", {"400", "429", "503"}),
        ("/api/etapes/a-valider", {"400", "403", "429", "503"}),
        ("/api/activite", {"400", "403", "429", "503"}),
    ],
)
def test_les_erreurs_possibles_de_chaque_route_sont_documentees(
    client: TestClient, chemin: str, statuts: set[str]
) -> None:
    operations = schema_openapi(client)["paths"][chemin]
    documentes = {statut for operation in operations.values() for statut in operation["responses"]}

    assert statuts <= documentes


def test_les_429_annoncent_l_en_tete_retry_after(client: TestClient) -> None:
    reponses = [
        reponse
        for _, _, statut, reponse in reponses_declarees(schema_openapi(client))
        if statut == "429"
    ]

    assert reponses
    assert all("Retry-After" in reponse["headers"] for reponse in reponses)


def test_les_413_ne_sont_declares_que_sur_les_routes_qui_recoivent_un_corps(
    client: TestClient,
) -> None:
    routes_413 = {
        (chemin, methode)
        for chemin, methode, statut, _ in reponses_declarees(schema_openapi(client))
        if statut == "413"
    }

    assert routes_413 == {
        ("/api/chantiers", "post"),
        ("/api/chantiers/{chantier_id}/etapes", "post"),
        ("/api/etapes/{etape_id}/transitions", "post"),
    }


def test_la_sonde_de_sante_n_est_pas_limitee(client: TestClient) -> None:
    operation = schema_openapi(client)["paths"]["/api/health"]["get"]

    assert "429" not in operation["responses"]


def test_les_descriptions_des_400_et_403_couvrent_les_middlewares(client: TestClient) -> None:
    descriptions = {
        statut: reponse["description"]
        for _, _, statut, reponse in reponses_declarees(schema_openapi(client))
        if statut in {"400", "403"}
    }

    assert "nom d'hôte" in descriptions["400"]
    assert "adresse bloquée" in descriptions["403"]
