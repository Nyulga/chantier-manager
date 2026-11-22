"""Fabrique un faux projet pour vérifier que import-linter échoue sur une violation.

On copie le package `app` et la configuration réelle (`pyproject.toml`) dans un
dossier temporaire, on y ajoute un fichier fautif, puis on lance import-linter
dans ce dossier. Le code réel du projet n'est jamais modifié, et les contrats
testés sont exactement ceux de la CI.

Import-linter est appelé dans le processus des tests plutôt que par un sous-processus :
c'est plus rapide, et cela évite d'exécuter un programme externe depuis les tests.
"""

import importlib
import shutil
import sys
from pathlib import Path

import pytest
from importlinter.cli import lint_imports

RACINE_BACKEND = Path(__file__).resolve().parents[2]
NOM_FICHIER_FAUTIF = "fichier_fautif.py"
PACKAGE_RACINE = "app"


def preparer_projet(dossier: Path, fichier_fautif: str | None = None, contenu: str = "") -> None:
    """Copie `app` et `pyproject.toml` dans `dossier`, avec en option un fichier fautif.

    Args:
        dossier: dossier temporaire vide qui accueille la copie.
        fichier_fautif: chemin du fichier à ajouter, relatif au package `app`.
        contenu: code du fichier fautif.
    """
    shutil.copytree(
        RACINE_BACKEND / PACKAGE_RACINE,
        dossier / PACKAGE_RACINE,
        ignore=shutil.ignore_patterns("__pycache__"),
    )
    shutil.copy(RACINE_BACKEND / "pyproject.toml", dossier / "pyproject.toml")
    if fichier_fautif is not None:
        (dossier / PACKAGE_RACINE / fichier_fautif).write_text(contenu, encoding="utf-8")


def _se_placer_dans_le_projet(dossier: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Fait pointer `import app` vers la copie temporaire, le temps du test.

    Import-linter cherche le package `app` comme le ferait `import app` : on se place
    dans le dossier temporaire, on le met en tête de `sys.path`, et on retire de
    `sys.modules` le vrai `app` déjà chargé par d'autres tests. Le monkeypatch remet
    tout en place à la fin du test.
    """
    monkeypatch.chdir(dossier)
    monkeypatch.setattr(sys, "path", [str(dossier), *sys.path])
    for nom in [nom for nom in sys.modules if nom.split(".")[0] == PACKAGE_RACINE]:
        monkeypatch.delitem(sys.modules, nom)
    importlib.invalidate_caches()


def lancer_lint_imports(dossier: Path, contrat: str, monkeypatch: pytest.MonkeyPatch) -> int:
    """Lance import-linter sur un seul contrat de la copie, et renvoie son code de sortie.

    Un seul contrat à la fois : l'échec prouve que *ce* contrat détecte la violation,
    et qu'un autre contrat ne la détecte pas à sa place.
    """
    _se_placer_dans_le_projet(dossier, monkeypatch)
    return lint_imports(
        config_filename=str(dossier / "pyproject.toml"),
        limit_to_contracts=(contrat,),
        no_cache=True,
        no_logo=True,
    )
