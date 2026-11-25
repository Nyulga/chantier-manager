"""Le champ piège des schémas d'entrée est facultatif et ne se signale pas dans OpenAPI."""

import pytest
from pydantic import BaseModel

from app.chantiers.api.schemas import CreerChantierRequete
from app.etapes.api.schemas import AjouterEtapeRequete
from app.shared.api.champ_piege import NOM_CHAMP_PIEGE


@pytest.mark.parametrize("schema", [CreerChantierRequete, AjouterEtapeRequete])
def test_le_champ_piege_est_facultatif_et_sans_description_qui_le_trahit(
    schema: type[BaseModel],
) -> None:
    json_schema = schema.model_json_schema()

    assert NOM_CHAMP_PIEGE not in json_schema["required"]
    texte = str(json_schema["properties"][NOM_CHAMP_PIEGE]).lower()
    assert "piège" not in texte
    assert "piege" not in texte
    assert "ne pas remplir" not in texte
