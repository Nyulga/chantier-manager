"""Prouve que le contrôle des tailles échoue sur un code trop long, et que le projet le respecte.

Les limites viennent de la règle 00 (§4) : 300 lignes par fichier, 40 par fonction.
"""

from pathlib import Path

from tests.architecture.projet_temporaire import RACINE_BACKEND
from tools.verifier_tailles import CODE_VIOLATION, MAX_LIGNES_FICHIER, MAX_LIGNES_FONCTION, main


def test_un_fichier_de_trop_de_lignes_fait_echouer_le_controle(tmp_path: Path) -> None:
    (tmp_path / "trop_long.py").write_text("x = 1\n" * (MAX_LIGNES_FICHIER + 1), encoding="utf-8")

    code = main([str(tmp_path)])

    assert code == CODE_VIOLATION


def test_une_fonction_de_trop_de_lignes_fait_echouer_le_controle(tmp_path: Path) -> None:
    source = "def trop_longue() -> None:\n" + "    pass\n" * MAX_LIGNES_FONCTION
    (tmp_path / "fonction_longue.py").write_text(source, encoding="utf-8")

    code = main([str(tmp_path)])

    assert code == CODE_VIOLATION


def test_le_code_du_projet_respecte_les_limites_de_taille() -> None:
    dossiers = [str(RACINE_BACKEND / nom) for nom in ("app", "tools", "tests")]

    code = main(dossiers)

    assert code == 0
