"""Le budget d'entrée est un texte décimal : le schéma OpenAPI le dit, le flottant est refusé."""

from app.chantiers.api.schemas import CreerChantierRequete


def test_le_budget_d_entree_est_un_texte_dans_le_schema_openapi() -> None:
    propriete = CreerChantierRequete.model_json_schema()["properties"]["budget"]

    assert propriete["type"] == "string"
