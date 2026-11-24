"""Outil de mesure des tailles : fichiers et fonctions au-delà des limites de la règle 00."""

import runpy
import sys
from pathlib import Path

import pytest

from tools.verifier_tailles import (
    CODE_CHEMIN_INTROUVABLE,
    CODE_VIOLATION,
    MAX_LIGNES_FICHIER,
    MAX_LIGNES_FONCTION,
    main,
    verifier,
    verifier_fichier,
)

LIGNE_DE_LA_FONCTION = 2
SCRIPT = Path(__file__).resolve().parents[2] / "tools" / "verifier_tailles.py"


def ecrire_fichier(dossier: Path, nom: str, contenu: str) -> Path:
    chemin = dossier / nom
    chemin.write_text(contenu, encoding="utf-8")
    return chemin


def fonction_de(nombre_de_lignes: int) -> str:
    """Source d'une fonction qui occupe exactement `nombre_de_lignes` lignes."""
    return "def f() -> None:\n" + "    pass\n" * (nombre_de_lignes - 1)


def test_un_fichier_a_la_limite_est_accepte(tmp_path: Path) -> None:
    chemin = ecrire_fichier(tmp_path, "limite.py", "x = 1\n" * MAX_LIGNES_FICHIER)

    assert verifier_fichier(chemin) == []


def test_un_fichier_trop_long_est_signale(tmp_path: Path) -> None:
    chemin = ecrire_fichier(tmp_path, "long.py", "x = 1\n" * (MAX_LIGNES_FICHIER + 1))

    violations = verifier_fichier(chemin)

    assert len(violations) == 1
    assert violations[0].chemin == chemin
    assert "301 lignes" in violations[0].message


def test_une_fonction_a_la_limite_est_acceptee(tmp_path: Path) -> None:
    chemin = ecrire_fichier(tmp_path, "limite.py", fonction_de(MAX_LIGNES_FONCTION))

    assert verifier_fichier(chemin) == []


def test_une_fonction_trop_longue_est_signalee_avec_sa_ligne(tmp_path: Path) -> None:
    source = "x = 1\n" + fonction_de(MAX_LIGNES_FONCTION + 1)
    chemin = ecrire_fichier(tmp_path, "longue.py", source)

    violations = verifier_fichier(chemin)

    assert len(violations) == 1
    assert violations[0].ligne == LIGNE_DE_LA_FONCTION
    assert "f" in violations[0].message
    assert "41 lignes" in violations[0].message


def test_une_methode_et_une_fonction_asynchrone_trop_longues_sont_signalees(
    tmp_path: Path,
) -> None:
    corps = "        pass\n" * MAX_LIGNES_FONCTION
    source = f"class A:\n    def methode(self) -> None:\n{corps}\nasync def g() -> None:\n{corps}"
    chemin = ecrire_fichier(tmp_path, "classe.py", source)

    violations = verifier_fichier(chemin)

    assert [v.ligne for v in violations] == [2, MAX_LIGNES_FONCTION + 4]


def test_un_fichier_a_la_syntaxe_invalide_est_signale_sans_planter(tmp_path: Path) -> None:
    chemin = ecrire_fichier(tmp_path, "casse.py", "def (:\n")

    violations = verifier_fichier(chemin)

    assert len(violations) == 1
    assert "syntaxe" in violations[0].message


def test_verifier_parcourt_les_sous_dossiers_et_ignore_le_reste(tmp_path: Path) -> None:
    (tmp_path / "paquet").mkdir()
    (tmp_path / ".venv").mkdir()
    ecrire_fichier(tmp_path / "paquet", "long.py", "x = 1\n" * (MAX_LIGNES_FICHIER + 1))
    ecrire_fichier(tmp_path / ".venv", "ignore.py", "x = 1\n" * (MAX_LIGNES_FICHIER + 1))
    ecrire_fichier(tmp_path, "notes.txt", "x\n" * (MAX_LIGNES_FICHIER + 1))

    violations = verifier([tmp_path])

    assert [v.chemin.name for v in violations] == ["long.py"]


def test_verifier_accepte_un_fichier_donne_directement(tmp_path: Path) -> None:
    chemin = ecrire_fichier(tmp_path, "long.py", "x = 1\n" * (MAX_LIGNES_FICHIER + 1))

    assert len(verifier([chemin])) == 1


def test_main_renvoie_zero_quand_tout_est_conforme(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    ecrire_fichier(tmp_path, "propre.py", "x = 1\n")

    code = main([str(tmp_path)])

    assert code == 0
    assert "conformes" in capsys.readouterr().out


def test_main_renvoie_un_et_liste_les_violations(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    chemin = ecrire_fichier(tmp_path, "long.py", "x = 1\n" * (MAX_LIGNES_FICHIER + 1))

    code = main([str(tmp_path)])

    sortie = capsys.readouterr().out
    assert code == CODE_VIOLATION
    assert f"{chemin}:1:" in sortie


def test_main_refuse_un_chemin_inexistant_pour_ne_pas_conclure_a_tort(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    code = main([str(tmp_path / "absent")])

    assert code == CODE_CHEMIN_INTROUVABLE
    assert "introuvable" in capsys.readouterr().err


def test_main_sans_argument_verifie_les_dossiers_du_backend(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    (tmp_path / "app").mkdir()
    (tmp_path / "tools").mkdir()
    (tmp_path / "tests").mkdir()
    monkeypatch.chdir(tmp_path)

    assert main([]) == 0


def test_le_script_se_lance_directement_en_ligne_de_commande(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    ecrire_fichier(tmp_path, "long.py", "x = 1\n" * (MAX_LIGNES_FICHIER + 1))
    monkeypatch.setattr(sys, "argv", [str(SCRIPT), str(tmp_path)])

    with pytest.raises(SystemExit) as sortie:
        runpy.run_path(str(SCRIPT), run_name="__main__")

    assert sortie.value.code == CODE_VIOLATION
