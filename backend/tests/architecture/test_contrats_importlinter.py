"""Prouve que chaque contrat import-linter échoue sur une violation volontaire.

Un garde-fou n'existe que lorsqu'on l'a vu échouer (ADR 0005). Chaque cas ci-dessous
ajoute dans une copie du projet un fichier qui viole un contrat précis ; le test
vérifie que `lint-imports` échoue sur ce contrat, alors qu'il réussit sans la violation.
"""

import tomllib
from dataclasses import dataclass
from pathlib import Path

import pytest

from tests.architecture.projet_temporaire import (
    NOM_FICHIER_FAUTIF,
    RACINE_BACKEND,
    lancer_lint_imports,
    preparer_projet,
)


@dataclass(frozen=True)
class Violation:
    """Un fichier fautif à ajouter dans `app`, et le contrat qu'il doit casser."""

    contrat: str
    dossier: str
    contenu: str


VIOLATIONS = {
    "le domaine importe l'application": Violation(
        "couches", "chantiers/domain", "import app.chantiers.application\n"
    ),
    "l'application importe l'api": Violation(
        "couches", "etapes/application", "import app.etapes.api\n"
    ),
    "l'api importe l'infrastructure de son module": Violation(
        "couches", "etapes/api", "import app.etapes.infrastructure\n"
    ),
    "l'infrastructure importe l'api": Violation(
        "couches", "shared/infrastructure", "import app.shared.api\n"
    ),
    "le domaine importe fastapi": Violation("domaine-pur", "chantiers/domain", "import fastapi\n"),
    "le domaine importe pydantic": Violation("domaine-pur", "etapes/domain", "import pydantic\n"),
    "le domaine importe sqlalchemy": Violation(
        "domaine-pur", "shared/domain", "import sqlalchemy\n"
    ),
    "le domaine importe psycopg": Violation("domaine-pur", "etapes/domain", "import psycopg\n"),
    "le domaine importe alembic": Violation("domaine-pur", "chantiers/domain", "import alembic\n"),
    "l'application importe sqlalchemy": Violation(
        "base-reservee", "chantiers/application", "import sqlalchemy\n"
    ),
    "l'api importe psycopg": Violation("base-reservee", "etapes/api", "import psycopg\n"),
    "une commande importe sqlalchemy": Violation("base-reservee", "cli", "import sqlalchemy\n"),
    "une route importe l'infrastructure de shared": Violation(
        "infrastructure-reservee", "chantiers/api", "import app.shared.infrastructure\n"
    ),
    "un service importe l'infrastructure d'un autre module": Violation(
        "infrastructure-reservee", "etapes/application", "import app.chantiers.infrastructure\n"
    ),
    "une route importe le domaine de son module": Violation(
        "api-sans-domain", "chantiers/api", "import app.chantiers.domain\n"
    ),
    "une route importe le domaine de shared": Violation(
        "api-sans-domain", "etapes/api", "import app.shared.domain\n"
    ),
    "shared importe chantiers": Violation(
        "shared-sans-metier", "shared/application", "import app.chantiers.application\n"
    ),
    "shared importe etapes": Violation(
        "shared-sans-metier", "shared/domain", "import app.etapes.domain\n"
    ),
    "chantiers importe etapes": Violation(
        "chantiers-sans-etapes", "chantiers/application", "import app.etapes.application\n"
    ),
    "etapes importe le domaine de chantiers": Violation(
        "etapes-via-application", "etapes/application", "import app.chantiers.domain\n"
    ),
    "etapes importe l'infrastructure de chantiers": Violation(
        "etapes-via-application", "etapes/infrastructure", "import app.chantiers.infrastructure\n"
    ),
}


def identifiants_des_contrats() -> set[str]:
    """Lit les identifiants des contrats déclarés dans le `pyproject.toml` réel."""
    configuration = tomllib.loads((RACINE_BACKEND / "pyproject.toml").read_text(encoding="utf-8"))
    contrats = configuration["tool"]["importlinter"]["contracts"]
    return {contrat["id"] for contrat in contrats}


def codes_de_sortie_de_tous_les_contrats(
    dossier: Path, monkeypatch: pytest.MonkeyPatch
) -> list[int]:
    """Lance chaque contrat séparément et renvoie leurs codes de sortie."""
    contrats = sorted(identifiants_des_contrats())
    return [lancer_lint_imports(dossier, contrat, monkeypatch) for contrat in contrats]


def test_le_projet_sans_violation_respecte_tous_les_contrats(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    preparer_projet(tmp_path)

    codes = codes_de_sortie_de_tous_les_contrats(tmp_path, monkeypatch)

    assert set(codes) == {0}


@pytest.mark.parametrize("violation", VIOLATIONS.values(), ids=VIOLATIONS.keys())
def test_une_violation_fait_echouer_son_contrat(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    violation: Violation,
) -> None:
    fichier = f"{violation.dossier}/{NOM_FICHIER_FAUTIF}"
    preparer_projet(tmp_path, fichier, violation.contenu)

    code = lancer_lint_imports(tmp_path, violation.contrat, monkeypatch)

    assert code != 0
    assert "BROKEN" in capsys.readouterr().out


def test_etapes_peut_utiliser_la_partie_application_de_chantiers(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Cas autorisé : il prouve que les contrats ne sont pas plus sévères que la règle.
    fichier = f"etapes/application/{NOM_FICHIER_FAUTIF}"
    preparer_projet(tmp_path, fichier, "import app.chantiers.application\n")

    codes = codes_de_sortie_de_tous_les_contrats(tmp_path, monkeypatch)

    assert set(codes) == {0}


def test_chaque_contrat_du_projet_a_une_violation_testee() -> None:
    contrats_testes = {violation.contrat for violation in VIOLATIONS.values()}

    assert contrats_testes == identifiants_des_contrats()
