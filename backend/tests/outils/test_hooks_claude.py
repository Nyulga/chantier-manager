"""Hooks de Claude Code du projet (`.claude/hooks/`) : branche dev et fichiers de secrets.

Chaque hook est exécuté comme un script, dans le processus du test : le JSON de l'appel arrive
sur l'entrée standard et le dossier du projet dans `CLAUDE_PROJECT_DIR`. Le code 2 bloque
l'appel ; le code 0 le laisse faire.
"""

import io
import json
import runpy
import sys
from pathlib import Path

import pytest

DOSSIER_HOOKS = Path(__file__).resolve().parents[3] / ".claude" / "hooks"
CODE_BLOQUER = 2
MESSAGE_BRANCHE = b"seulement sur la branche dev"
MESSAGE_SECRETS = b"fichier de secrets"


def lancer(script: str, entree: object, monkeypatch: pytest.MonkeyPatch) -> tuple[int, bytes]:
    """Exécute le hook `script` avec `entree` en JSON ; renvoie son code et sa sortie d'erreur."""
    octets_erreur = io.BytesIO()
    erreur = io.TextIOWrapper(octets_erreur, encoding="utf-8")
    monkeypatch.setattr(sys, "stdin", io.TextIOWrapper(io.BytesIO(json.dumps(entree).encode())))
    monkeypatch.setattr(sys, "stderr", erreur)

    with pytest.raises(SystemExit) as fin:
        runpy.run_path(str(DOSSIER_HOOKS / script), run_name="__main__")

    erreur.flush()
    code = fin.value.code
    return (code if isinstance(code, int) else 0), octets_erreur.getvalue()


def bash(texte: str) -> dict[str, object]:
    """Entrée d'un appel à l'outil Bash."""
    return {"tool_name": "Bash", "tool_input": {"command": texte}}


@pytest.fixture
def projet(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Dossier de projet vide, désigné par `CLAUDE_PROJECT_DIR`."""
    monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(tmp_path))
    return tmp_path


def sur_la_branche(projet: Path, tete: str) -> None:
    """Écrit `.git/HEAD` comme le fait git : `ref: refs/heads/<branche>` ou un commit."""
    (projet / ".git").mkdir()
    (projet / ".git" / "HEAD").write_text(f"{tete}\n", encoding="utf-8")


@pytest.mark.parametrize(
    "texte",
    [
        "git commit -m x",
        "git push origin autre",
        "git -C . commit -m x",
        "cd backend && git commit -m x",
        'git commit -q -F "message.txt"',
    ],
)
def test_un_commit_ou_un_push_hors_de_dev_est_bloque(
    projet: Path, monkeypatch: pytest.MonkeyPatch, texte: str
) -> None:
    sur_la_branche(projet, "ref: refs/heads/autre")

    code, erreur = lancer("commit_sur_dev.py", bash(texte), monkeypatch)

    assert code == CODE_BLOQUER
    assert MESSAGE_BRANCHE in erreur


@pytest.mark.parametrize("tete", ["0123456789abcdef0123456789abcdef01234567", "ref: refs/heads/"])
def test_un_commit_sur_une_branche_inconnue_est_bloque(
    projet: Path, monkeypatch: pytest.MonkeyPatch, tete: str
) -> None:
    sur_la_branche(projet, tete)

    code, erreur = lancer("commit_sur_dev.py", bash("git commit -m x"), monkeypatch)

    assert code == CODE_BLOQUER
    assert b"inconnue" in erreur


def test_un_commit_sans_depot_git_est_bloque(projet: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    assert lancer("commit_sur_dev.py", bash("git commit -m x"), monkeypatch)[0] == CODE_BLOQUER


@pytest.mark.parametrize("texte", ["git commit -m x", "git push origin dev"])
def test_un_commit_ou_un_push_sur_dev_est_permis(
    projet: Path, monkeypatch: pytest.MonkeyPatch, texte: str
) -> None:
    sur_la_branche(projet, "ref: refs/heads/dev")

    assert lancer("commit_sur_dev.py", bash(texte), monkeypatch) == (0, b"")


@pytest.mark.parametrize(
    "texte", ["git checkout main && git commit -m x", "git switch main; git push"]
)
def test_un_changement_de_branche_suivi_dun_commit_est_bloque(
    projet: Path, monkeypatch: pytest.MonkeyPatch, texte: str
) -> None:
    sur_la_branche(projet, "ref: refs/heads/dev")

    code, erreur = lancer("commit_sur_dev.py", bash(texte), monkeypatch)

    assert code == CODE_BLOQUER
    assert MESSAGE_BRANCHE in erreur


@pytest.mark.parametrize("texte", ["git status", "ls", "echo commit", "git log -3"])
def test_les_autres_commandes_sont_permises_hors_de_dev(
    projet: Path, monkeypatch: pytest.MonkeyPatch, texte: str
) -> None:
    sur_la_branche(projet, "ref: refs/heads/autre")

    assert lancer("commit_sur_dev.py", bash(texte), monkeypatch) == (0, b"")


@pytest.mark.parametrize("script", ["commit_sur_dev.py", "secrets_hors_terminal.py"])
@pytest.mark.parametrize(
    "entree",
    [
        {"tool_name": "Write", "tool_input": {}},
        [],
        "x",
        {"tool_name": "Bash", "tool_input": {"command": ["git", "commit"]}},
    ],
)
def test_un_hook_ignore_une_entree_sans_commande(
    projet: Path, monkeypatch: pytest.MonkeyPatch, script: str, entree: object
) -> None:
    assert lancer(script, entree, monkeypatch) == (0, b"")


@pytest.mark.parametrize(
    "texte",
    [
        "cat .env",
        "cat backend/.env.local",
        "type deploy\\.env",
        "source .env",
        "cp .env.production x",
        "python -c \"print(open('.env').read())\"",
        "grep x ~/.claude.json",
        "ls ~/.ssh",
        "cat ~/.ssh/id_ed25519",
    ],
)
def test_une_commande_qui_nomme_un_fichier_de_secrets_est_bloquee(
    projet: Path, monkeypatch: pytest.MonkeyPatch, texte: str
) -> None:
    code, erreur = lancer("secrets_hors_terminal.py", bash(texte), monkeypatch)

    assert code == CODE_BLOQUER
    assert MESSAGE_SECRETS in erreur


@pytest.mark.parametrize(
    "texte",
    [
        "cat backend/migrations/env.py",
        "cat .env.example",
        "ls .envrc",
        "cat .claude/settings.json",
        "grep -rn enveloppe src",
        "git status",
    ],
)
def test_une_commande_sans_fichier_de_secrets_est_permise(
    projet: Path, monkeypatch: pytest.MonkeyPatch, texte: str
) -> None:
    assert lancer("secrets_hors_terminal.py", bash(texte), monkeypatch) == (0, b"")
