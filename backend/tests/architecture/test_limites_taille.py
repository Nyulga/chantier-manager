"""Prouve que le contrôle des tailles échoue sur un code trop long, et que le projet le respecte.

Les limites viennent de la règle 00 (§4) : 300 lignes par fichier, 40 par fonction et
3 niveaux d'imbrication de blocs par fonction.
"""

import textwrap
from pathlib import Path

import pytest

from tests.architecture.projet_temporaire import RACINE_BACKEND
from tools.verifier_tailles import (
    CODE_VIOLATION,
    MAX_LIGNES_FICHIER,
    MAX_LIGNES_FONCTION,
    main,
)

TROIS_NIVEAUX = """
def f(x: bool) -> None:
    if x:
        if x:
            if x:
                pass
"""

QUATRE_NIVEAUX_DE_IF = """
def f(x: bool) -> None:
    if x:
        if x:
            if x:
                if x:
                    pass
"""


def _ecrire_et_verifier(tmp_path: Path, source: str) -> int:
    """Écrit le code donné (indenté pour la lisibilité) dans un fichier, puis le contrôle."""
    (tmp_path / "exemple.py").write_text(textwrap.dedent(source), encoding="utf-8")
    return main([str(tmp_path)])


def test_un_fichier_de_trop_de_lignes_fait_echouer_le_controle(tmp_path: Path) -> None:
    (tmp_path / "trop_long.py").write_text("x = 1\n" * (MAX_LIGNES_FICHIER + 1), encoding="utf-8")

    code = main([str(tmp_path)])

    assert code == CODE_VIOLATION


def test_une_fonction_de_trop_de_lignes_fait_echouer_le_controle(tmp_path: Path) -> None:
    source = "def trop_longue() -> None:\n" + "    pass\n" * MAX_LIGNES_FONCTION
    (tmp_path / "fonction_longue.py").write_text(source, encoding="utf-8")

    code = main([str(tmp_path)])

    assert code == CODE_VIOLATION


def test_une_fonction_trop_imbriquee_fait_echouer_le_controle_et_donne_la_ligne(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    code = _ecrire_et_verifier(tmp_path, QUATRE_NIVEAUX_DE_IF)

    assert code == CODE_VIOLATION
    assert "exemple.py:6:" in capsys.readouterr().out


def test_une_fonction_a_la_profondeur_maximale_passe(tmp_path: Path) -> None:
    code = _ecrire_et_verifier(tmp_path, TROIS_NIVEAUX)

    assert code == 0


# Chaque source place un bloc d'une sorte différente au quatrième niveau, sous trois `if`.
QUATRIEME_NIVEAU = [
    """
    def f(x: bool) -> None:
        if x:
            if x:
                if x:
                    for y in x:
                        pass
    """,
    """
    def f(x: bool) -> None:
        if x:
            if x:
                if x:
                    while x:
                        pass
    """,
    """
    def f(x: bool) -> None:
        if x:
            if x:
                if x:
                    with x:
                        pass
    """,
    """
    def f(x: bool) -> None:
        if x:
            if x:
                if x:
                    try:
                        pass
                    finally:
                        pass
    """,
    """
    def f(x: bool) -> None:
        if x:
            if x:
                if x:
                    match x:
                        case _:
                            pass
    """,
]


@pytest.mark.parametrize("source", QUATRIEME_NIVEAU)
def test_chaque_sorte_de_bloc_compte_dans_la_profondeur(tmp_path: Path, source: str) -> None:
    code = _ecrire_et_verifier(tmp_path, source)

    assert code == CODE_VIOLATION


def test_une_chaine_de_elif_ne_compte_pas_comme_une_imbrication(tmp_path: Path) -> None:
    code = _ecrire_et_verifier(
        tmp_path,
        """
        def f(x: int) -> None:
            if x == 1:
                if x:
                    if x:
                        pass
            elif x == 2:
                pass
            elif x == 3:
                pass
            elif x == 4:
                if x:
                    if x:
                        pass
            else:
                pass
        """,
    )

    assert code == 0


def test_un_else_qui_contient_un_if_compte_comme_une_imbrication(tmp_path: Path) -> None:
    code = _ecrire_et_verifier(
        tmp_path,
        """
        def f(x: int) -> None:
            if x:
                pass
            else:
                if x:
                    if x:
                        if x:
                            pass
        """,
    )

    assert code == CODE_VIOLATION


def test_une_fonction_interne_est_mesuree_a_part(tmp_path: Path) -> None:
    code = _ecrire_et_verifier(
        tmp_path,
        """
        def externe(x: bool) -> None:
            if x:
                if x:
                    def interne() -> None:
                        if x:
                            pass
        """,
    )

    assert code == 0


def test_le_code_du_projet_respecte_les_limites_de_taille() -> None:
    dossiers = [str(RACINE_BACKEND / nom) for nom in ("app", "tools", "tests")]

    code = main(dossiers)

    assert code == 0
