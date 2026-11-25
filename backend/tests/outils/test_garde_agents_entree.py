"""Garde des sous-agents : entrées illisibles, pannes, réponse et script de bout en bout."""

import io
import json
import runpy
import sys
from pathlib import Path

import pytest

from tests.outils.appels_garde_agents import RACINE, commande, ecriture
from tools.garde import protocole
from tools.garde.protocole import CODE_BLOQUER, EntreeIllisibleError, decider, traiter

CODE_DOCUMENTE = 2  # Le seul code que Claude Code lit comme « bloquer l'appel ».
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
def test_une_entree_illisible_est_bloquee_avec_une_raison(brut: bytes) -> None:
    reponse = traiter(brut, RACINE)

    assert reponse.code == CODE_BLOQUER == CODE_DOCUMENTE
    assert reponse.sortie == ""
    assert "illisible" in reponse.erreur


def test_une_erreur_inattendue_de_la_garde_bloque_lappel(monkeypatch: pytest.MonkeyPatch) -> None:
    def en_panne(entree: object, racine: str | Path) -> str | None:
        raise RecursionError

    monkeypatch.setattr(protocole, "decider", en_panne)
    brut = json.dumps(commande("dev-api", "git status")).encode()

    reponse = traiter(brut, RACINE)

    assert reponse.code == CODE_BLOQUER
    assert "RecursionError" in reponse.erreur


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
    racine: str | None = RACINE,
) -> tuple[int | str | None, str, bytes]:
    """Exécute le script comme `python garde_agents.py`, avec `entree` sur l'entrée standard.

    `racine` est la valeur de `CLAUDE_PROJECT_DIR` ; `None` retire la variable. La sortie
    d'erreur est capturée en octets, dans un flux à l'encodage de Windows (cp1252), pour
    vérifier que le script y écrit bien de l'UTF-8.
    """
    sortie = io.StringIO()
    octets_erreur = io.BytesIO()
    erreur = io.TextIOWrapper(octets_erreur, encoding="cp1252")
    monkeypatch.setattr(sys, "stdin", io.TextIOWrapper(io.BytesIO(json.dumps(entree).encode())))
    monkeypatch.setattr(sys, "stdout", sortie)
    monkeypatch.setattr(sys, "stderr", erreur)
    if racine is None:
        monkeypatch.delenv("CLAUDE_PROJECT_DIR", raising=False)
    else:
        monkeypatch.setenv("CLAUDE_PROJECT_DIR", racine)

    with pytest.raises(SystemExit) as fin:
        runpy.run_path(str(SCRIPT), run_name="__main__")

    erreur.flush()
    return fin.value.code, sortie.getvalue(), octets_erreur.getvalue()


def test_le_script_de_bout_en_bout_refuse_un_ecart_de_couche(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    entree = ecriture("dev-metier", "backend/app/etapes/api/routes.py")

    code, sortie, erreur = lancer_le_script(entree, monkeypatch)

    assert code == 0
    assert json.loads(sortie)["hookSpecificOutput"]["permissionDecision"] == "deny"
    assert erreur == b""


def test_le_script_de_bout_en_bout_laisse_passer_la_session_principale(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    entree = {"tool_name": "Bash", "tool_input": {"command": "git commit -m x"}}

    assert lancer_le_script(entree, monkeypatch) == (0, "", b"")


def test_le_script_bloque_une_entree_mal_formee_avec_un_message_en_utf8(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    code, sortie, erreur = lancer_le_script(["pas", "un", "objet"], monkeypatch)

    assert code == CODE_DOCUMENTE
    assert sortie == ""
    assert "entrée illisible".encode() in erreur


def test_un_python_trop_ancien_bloque_les_sous_agents(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(sys, "version_info", (3, 12, 9))
    entree = ecriture("dev-metier", "backend/app/etapes/domain/etape.py")

    code, sortie, erreur = lancer_le_script(entree, monkeypatch)

    assert code == CODE_DOCUMENTE
    assert sortie == ""
    assert b"3.13" in erreur


def test_un_python_trop_ancien_laisse_passer_la_session_principale(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(sys, "version_info", (3, 12, 9))
    entree = {"tool_name": "Write", "tool_input": {"file_path": f"{RACINE}/x.py"}}

    assert lancer_le_script(entree, monkeypatch) == (0, "", b"")


def test_une_garde_impossible_a_charger_bloque_les_sous_agents(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setitem(sys.modules, "tools.garde.protocole", None)
    entree = ecriture("dev-metier", "backend/app/etapes/domain/etape.py")

    code, _, erreur = lancer_le_script(entree, monkeypatch)

    assert code == CODE_DOCUMENTE
    assert b"erreur interne" in erreur


def test_sans_variable_denvironnement_la_racine_est_celle_du_depot(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    depot = SCRIPT.parents[2].as_posix()
    entree = {
        "agent_type": "dev-metier",
        "tool_name": "Write",
        "tool_input": {"file_path": f"{depot}/backend/app/etapes/domain/x.py"},
    }

    assert lancer_le_script(entree, monkeypatch, racine=None) == (0, "", b"")
