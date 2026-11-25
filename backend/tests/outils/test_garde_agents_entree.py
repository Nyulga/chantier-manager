"""Garde des sous-agents : entrées illisibles, format de la réponse et script de bout en bout."""

import io
import json
import runpy
import sys
from pathlib import Path

import pytest

from tests.outils.appels_garde_agents import RACINE, commande, ecriture
from tools.garde_agents import CODE_ENTREE_ILLISIBLE, EntreeIllisibleError, decider, traiter

CODE_DOCUMENTE = 2  # Le code que Claude Code lit comme « bloquer l'appel ».
SCRIPT = Path(__file__).resolve().parents[2] / "tools" / "garde_agents.py"


@pytest.mark.parametrize(
    "entree",
    [
        [],
        "texte",
        {"agent_type": 3, "tool_name": "Write"},
        {"agent_type": "dev-api", "tool_name": 3},
        {"agent_type": "dev-api"},
        {"agent_type": "dev-api", "tool_name": "Write"},
        {"agent_type": "dev-api", "tool_name": "Write", "tool_input": []},
        {"agent_type": "dev-api", "tool_name": "Write", "tool_input": {"file_path": 3}},
        {"agent_type": "dev-api", "tool_name": "Edit", "tool_input": {}},
        {"agent_type": "dev-api", "tool_name": "Bash", "tool_input": {"command": ["git"]}},
    ],
)
def test_une_entree_mal_formee_leve_une_erreur(entree: object) -> None:
    with pytest.raises(EntreeIllisibleError):
        decider(entree, RACINE)


@pytest.mark.parametrize(
    "brut", [b"pas du json", b"", b"\xff\xfe", b'["liste"]', b'{"agent_type": 3}']
)
def test_une_entree_illisible_sort_avec_le_code_2_et_une_raison_sur_stderr(brut: bytes) -> None:
    reponse = traiter(brut, RACINE)

    assert reponse.code == CODE_ENTREE_ILLISIBLE == CODE_DOCUMENTE
    assert reponse.sortie == ""
    assert reponse.erreur.strip() != ""


def test_une_entree_autorisee_ne_produit_aucune_sortie() -> None:
    brut = json.dumps(ecriture("dev-metier", "backend/app/etapes/domain/etape.py")).encode()

    reponse = traiter(brut, RACINE)

    assert (reponse.code, reponse.sortie, reponse.erreur) == (0, "", "")


def test_un_refus_produit_la_decision_deny_au_format_de_claude_code() -> None:
    brut = json.dumps(commande("dev-api", "git push")).encode()

    reponse = traiter(brut, RACINE)

    decision = json.loads(reponse.sortie)["hookSpecificOutput"]
    assert reponse.code == 0
    assert decision["hookEventName"] == "PreToolUse"
    assert decision["permissionDecision"] == "deny"
    assert "coordinateur" in decision["permissionDecisionReason"]


def lancer_le_script(
    entree: object,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    racine: str | None = RACINE,
) -> tuple[int | str | None, str, str]:
    """Exécute le script comme `python garde_agents.py`, avec `entree` sur l'entrée standard.

    `racine` est la valeur de `CLAUDE_PROJECT_DIR` ; `None` retire la variable.
    """
    flux = io.TextIOWrapper(io.BytesIO(json.dumps(entree).encode("utf-8")))
    monkeypatch.setattr(sys, "stdin", flux)
    if racine is None:
        monkeypatch.delenv("CLAUDE_PROJECT_DIR", raising=False)
    else:
        monkeypatch.setenv("CLAUDE_PROJECT_DIR", racine)

    with pytest.raises(SystemExit) as sortie:
        runpy.run_path(str(SCRIPT), run_name="__main__")

    capture = capsys.readouterr()
    return sortie.value.code, capture.out, capture.err


def test_le_script_de_bout_en_bout_refuse_un_ecart_de_couche(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    entree = ecriture("dev-metier", "backend/app/etapes/api/routes.py")

    code, sortie, erreur = lancer_le_script(entree, monkeypatch, capsys)

    assert code == 0
    assert json.loads(sortie)["hookSpecificOutput"]["permissionDecision"] == "deny"
    assert erreur == ""


def test_le_script_de_bout_en_bout_laisse_passer_la_session_principale(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    entree = {"tool_name": "Bash", "tool_input": {"command": "git commit -m x"}}

    assert lancer_le_script(entree, monkeypatch, capsys) == (0, "", "")


def test_le_script_de_bout_en_bout_bloque_une_entree_mal_formee(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    code, sortie, erreur = lancer_le_script(["pas", "un", "objet"], monkeypatch, capsys)

    assert code == CODE_ENTREE_ILLISIBLE
    assert sortie == ""
    assert "objet JSON" in erreur


def test_sans_variable_denvironnement_la_racine_est_celle_du_depot(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    depot = SCRIPT.parents[2].as_posix()
    entree = {
        "agent_type": "dev-metier",
        "tool_name": "Write",
        "tool_input": {"file_path": f"{depot}/backend/app/etapes/domain/x.py"},
    }

    assert lancer_le_script(entree, monkeypatch, capsys, racine=None) == (0, "", "")
