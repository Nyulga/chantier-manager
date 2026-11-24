"""Prouve que le contrôle des désactivations échoue sur chaque contournement interdit.

La règle 00 (§4) interdit `# noqa`, `# type: ignore`, `# pragma: no cover` et `cast`
en Python. Chaque test écrit un projet temporaire fautif et vérifie que le contrôle
échoue en nommant le fichier et la ligne ; deux tests prouvent aussi qu'il ne se
laisse pas piéger par une chaîne de caractères et que le code réel est conforme.
"""

from pathlib import Path

import pytest

from tests.architecture.projet_temporaire import RACINE_BACKEND
from tools.verifier_desactivations import CODE_VIOLATION, RACINES_PAR_DEFAUT, main

FICHIER = "fautif.py"


def _lancer(tmp_path: Path, source: str) -> int:
    (tmp_path / FICHIER).write_text(source, encoding="utf-8")
    return main([str(tmp_path)])


@pytest.mark.parametrize(
    "source",
    [
        "import os  # noqa: F401\n",
        "x: int = 'a'  # type: ignore[assignment]\n",
        "def f() -> None:  # pragma: no cover\n    pass\n",
        "x = 1  # NOQA\n",
        "x = 1  # pragma:no branch\n",
        "x = 1  # nosec B101\n",
        "# mypy: ignore-errors\nx = 1\n",
        "from typing import cast\n",
        "from typing import Any, cast as convertir\n",
        "import typing\nx = typing.cast(int, 1)\n",
        "import typing as t\nx = t.cast(int, 1)\n",
    ],
)
def test_une_desactivation_interdite_fait_echouer_le_controle(
    tmp_path: Path, source: str, capsys: pytest.CaptureFixture[str]
) -> None:
    code = _lancer(tmp_path, source)

    assert code == CODE_VIOLATION
    assert f"{FICHIER}:" in capsys.readouterr().out


def test_la_violation_indique_le_fichier_et_la_ligne(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    source = "a = 1\nb = 2\nimport os  # noqa: F401\n"

    _lancer(tmp_path, source)

    assert f"{FICHIER}:3:" in capsys.readouterr().out


def test_un_fichier_propre_passe(tmp_path: Path) -> None:
    code = _lancer(tmp_path, "def f() -> int:\n    return 1  # Un commentaire ordinaire.\n")

    assert code == 0


def test_une_chaine_de_caracteres_ne_declenche_pas_le_controle(tmp_path: Path) -> None:
    source = 'MOTIF = "x = 1  # noqa"\nAIDE = """# type: ignore\n# pragma: no cover"""\n'

    code = _lancer(tmp_path, source)

    assert code == 0


def test_une_methode_nommee_cast_sur_un_autre_objet_passe(tmp_path: Path) -> None:
    code = _lancer(tmp_path, "x = valeur.cast(1)\n")

    assert code == 0


def test_un_fichier_a_la_syntaxe_invalide_ne_passe_pas_pour_conforme(tmp_path: Path) -> None:
    code = _lancer(tmp_path, "def (:\n")

    assert code == CODE_VIOLATION


def test_le_code_du_projet_ne_contient_aucune_desactivation() -> None:
    dossiers = [str(RACINE_BACKEND / nom) for nom in RACINES_PAR_DEFAUT]

    code = main(dossiers)

    assert code == 0
