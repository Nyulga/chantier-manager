"""Le champ piège des schémas d'entrée est facultatif et documenté « ne pas remplir »."""

import pytest
from pydantic import BaseModel

from app.chantiers.api.schemas import CreerChantierRequete
from app.etapes.api.schemas import AjouterEtapeRequete
from app.shared.api.champ_piege import NOM_CHAMP_PIEGE


@pytest.mark.parametrize("schema", [CreerChantierRequete, AjouterEtapeRequete])
def test_le_champ_piege_est_facultatif_et_documente(schema: type[BaseModel]) -> None:
    json_schema = schema.model_json_schema()

    assert NOM_CHAMP_PIEGE not in json_schema["required"]
    assert "ne pas remplir" in json_schema["properties"][NOM_CHAMP_PIEGE]["description"].lower()
