"""Outil des désactivations : chemins introuvables, valeurs par défaut et lancement direct."""

import runpy
import sys
from pathlib import Path

import pytest

from tools.verifier_desactivations import CODE_CHEMIN_INTROUVABLE, CODE_VIOLATION, main


def test_main_refuse_un_chemin_inexistant_pour_ne_pas_conclure_a_tort(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    code = main([str(tmp_path / "absent")])

    assert code == CODE_CHEMIN_INTROUVABLE
    assert "introuvable" in capsys.readouterr().err


def test_main_sans_argument_verifie_les_dossiers_du_backend(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    for nom in ("app", "tools", "migrations", "tests"):
        (tmp_path / nom).mkdir()
    monkeypatch.chdir(tmp_path)

    assert main([]) == 0


def test_le_module_se_lance_directement_en_ligne_de_commande(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    (tmp_path / "fautif.py").write_text("x = 1  # noqa\n", encoding="utf-8")
    monkeypatch.setattr(sys, "argv", ["verifier_desactivations", str(tmp_path)])

    with pytest.raises(SystemExit) as sortie:
        runpy.run_module("tools.verifier_desactivations", run_name="__main__")

    assert sortie.value.code == CODE_VIOLATION
