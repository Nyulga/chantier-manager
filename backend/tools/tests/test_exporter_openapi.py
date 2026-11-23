"""Outil d'export du schéma OpenAPI, source des types du frontend."""

import json
import runpy
import sys
from pathlib import Path

import pytest

from tools.exporter_openapi import CODE_USAGE, main, schema_openapi

SCRIPT = Path(__file__).resolve().parents[1] / "exporter_openapi.py"


def test_le_schema_decrit_la_route_de_sante() -> None:
    schema = json.loads(schema_openapi())

    assert "/api/health" in schema["paths"]


def test_le_schema_est_stable_d_une_execution_a_l_autre() -> None:
    assert schema_openapi() == schema_openapi()


def test_main_ecrit_le_schema_dans_le_fichier_demande(tmp_path: Path) -> None:
    sortie = tmp_path / "openapi.json"

    code = main([str(sortie)])

    assert code == 0
    assert sortie.read_text(encoding="utf-8") == schema_openapi()


@pytest.mark.parametrize("arguments", [[], ["a.json", "b.json"]])
def test_main_exige_exactement_un_chemin_de_sortie(arguments: list[str]) -> None:
    assert main(arguments) == CODE_USAGE


def test_le_script_peut_etre_lance_directement(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    sortie = tmp_path / "openapi.json"
    monkeypatch.setattr(sys, "argv", [str(SCRIPT), str(sortie)])

    with pytest.raises(SystemExit) as fin:
        runpy.run_path(str(SCRIPT), run_name="__main__")

    assert fin.value.code == 0
    assert sortie.exists()
