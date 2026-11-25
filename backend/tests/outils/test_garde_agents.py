"""Garde des sous-agents : droits d'écriture par couche, chemins et session principale."""

import pytest

from tests.outils.appels_garde_agents import RACINE, ecriture
from tools.garde.chemins import chemin_relatif
from tools.garde.protocole import decider

AGENTS_ECRIVAINS = ["dev-metier", "dev-donnees", "dev-api", "dev-frontend", "dev-socle"]
SANS_ECRITURE = ("revue", "conformite", "securite", "pentest", "backlog")


@pytest.mark.parametrize(
    ("agent", "relatif"),
    [
        ("dev-metier", "backend/app/etapes/domain/etape.py"),
        ("dev-metier", "backend/app/shared/application/x.py"),
        ("dev-metier", "backend/app/etapes/infrastructure/memoire/etape_repository.py"),
        ("dev-metier", "backend/app/shared/infrastructure/horloge_fixe_memoire.py"),
        ("dev-metier", "backend/tests/domain/etapes/test_cycle.py"),
        ("dev-metier", "backend/tests/fabriques/etapes.py"),
        ("dev-metier", "backend/tests/infrastructure/shared/test_limiteur_debit_memoire.py"),
        ("dev-metier", "backend/tests/infrastructure/etapes/test_memoire.py"),
        ("dev-donnees", "backend/app/etapes/infrastructure/sql/x.py"),
        ("dev-donnees", "backend/migrations/versions/0003_x.py"),
        ("dev-donnees", "backend/alembic.ini"),
        ("dev-donnees", "backend/app/main.py"),
        ("dev-donnees", "backend/tests/contrats/test_x.py"),
        ("dev-donnees", "backend/tests/conftest.py"),
        ("dev-api", "backend/app/etapes/api/routes.py"),
        ("dev-api", "backend/tests/api/etapes/test_routes.py"),
        ("dev-api", "backend/tests/integration/etapes/test_routes_etapes.py"),
        ("dev-api", "frontend/src/api/schema.d.ts"),
        ("dev-api", "frontend/openapi.json"),
        ("dev-frontend", "frontend/src/pages/x.tsx"),
        ("dev-frontend", "frontend/e2e/parcours.spec.ts"),
        ("dev-frontend", "frontend/tests/theme/x.test.ts"),
        ("dev-socle", "deploy/compose.prod.yaml"),
        ("dev-socle", ".github/workflows/ci.yml"),
        ("dev-socle", "justfile"),
        ("dev-socle", ".pre-commit-config.yaml"),
        ("dev-socle", "backend/tools/verifier_tailles.py"),
        ("dev-socle", "backend/tests/outils/test_verifier_tailles.py"),
        ("dev-socle", "backend/tests/architecture/test_x.py"),
        ("dev-socle", "backend/pyproject.toml"),
        ("dev-socle", "frontend/package.json"),
        ("dev-socle", "frontend/eslint/limites.js"),
        ("dev-socle", "frontend/tsconfig.app.json"),
        ("dev-socle", "frontend/tests/garde-fous/limites.test.ts"),
    ],
)
def test_un_agent_ecrit_dans_sa_couche(agent: str, relatif: str) -> None:
    assert decider(ecriture(agent, relatif), RACINE) is None


@pytest.mark.parametrize(
    ("agent", "relatif"),
    [
        ("dev-metier", "backend/app/shared/infrastructure/horloge_systeme.py"),
        ("dev-metier", "backend/app/etapes/infrastructure/sql/x.py"),
        ("dev-metier", "backend/app/etapes/api/routes.py"),
        ("dev-metier", "backend/tests/infrastructure/shared/test_uow_sql.py"),
        ("dev-metier", "justfile"),
        ("dev-donnees", "backend/app/etapes/domain/etape.py"),
        ("dev-donnees", "backend/app/etapes/api/routes.py"),
        ("dev-api", "backend/app/etapes/application/x.py"),
        ("dev-api", "backend/tests/domain/test_x.py"),
        ("dev-frontend", "backend/app/main.py"),
        ("dev-frontend", "frontend/src/api/schema.d.ts"),
        ("dev-frontend", "frontend/openapi.json"),
        ("dev-frontend", "frontend/eslint/limites.js"),
        ("dev-frontend", "frontend/eslint.config.js"),
        ("dev-frontend", "frontend/package.json"),
        ("dev-frontend", "frontend/vite.config.ts"),
        ("dev-frontend", "frontend/tsconfig.app.json"),
        ("dev-frontend", "frontend/tests/garde-fous/limites.test.ts"),
        ("dev-socle", "backend/app/etapes/domain/etape.py"),
        ("dev-socle", "docs/plan/squelette.md"),
        ("dev-socle", "frontend/src/pages/x.tsx"),
        ("dev-socle", "intent.md"),
    ],
)
def test_un_agent_ne_peut_pas_ecrire_hors_de_sa_couche(agent: str, relatif: str) -> None:
    raison = decider(ecriture(agent, relatif), RACINE)

    assert raison is not None
    assert agent in raison
    assert "coordinateur" in raison


@pytest.mark.parametrize("agent", [*AGENTS_ECRIVAINS, "general-purpose"])
@pytest.mark.parametrize(
    "chemin",
    [
        f"{RACINE}/.claude/settings.json",
        f"{RACINE}/.claude/agents/dev-metier.md",
        f"{RACINE}/backend/tools/garde_agents.py",
        f"{RACINE}/backend/tools/garde/droits.py",
        f"{RACINE}/backend/tools/garde/__init__.py",
        f"{RACINE}/backend/tests/outils/test_garde_agents.py",
        f"{RACINE}/backend/tests/outils/test_garde_agents_bash.py",
        f"{RACINE}/backend/tests/outils/appels_garde_agents.py",
        "C:/Users/X/.claude/settings.json",
        "C:/Users/X/.claude.json",
        "/home/x/.claude/agents/a.md",
        "/c/Users/X/Projet/.claude/settings.json",
    ],
)
def test_la_garde_et_claude_sont_proteges_pour_tous(agent: str, chemin: str) -> None:
    entree = {"agent_type": agent, "tool_name": "Write", "tool_input": {"file_path": chemin}}

    raison = decider(entree, RACINE)

    assert raison is not None
    assert "protégé" in raison


@pytest.mark.parametrize("agent", ["dev-socle", "general-purpose"])
@pytest.mark.parametrize(
    "chemin",
    [
        f"{RACINE}/backend/tools/garde_agents.py.",
        f"{RACINE}/backend/tools/garde_agents.py ",
        f"{RACINE}/backend/tools/garde_agents.py::$DATA",
        f"{RACINE}/backend/tools./garde_agents.py",
        "//serveur/partage/x.py",
        "\\\\?\\C:\\Users\\X\\Projet\\justfile",
    ],
)
def test_une_forme_de_chemin_que_windows_ramene_a_un_autre_fichier_est_refusee(
    agent: str, chemin: str
) -> None:
    entree = {"agent_type": agent, "tool_name": "Write", "tool_input": {"file_path": chemin}}

    raison = decider(entree, RACINE)

    assert raison is not None
    assert "forme de chemin" in raison


def test_dev_metier_ne_sort_pas_de_sa_couche_par_des_points_points() -> None:
    relatif = "backend/app/etapes/domain/../../shared/infrastructure/x.py"

    assert decider(ecriture("dev-metier", relatif), RACINE) is not None


def test_un_chemin_windows_avec_majuscules_et_antislashs_est_reconnu() -> None:
    entree = {
        "agent_type": "dev-metier",
        "tool_name": "Edit",
        "tool_input": {"file_path": "C:\\Users\\X\\Projet\\Backend\\App\\Etapes\\Domain\\x.py"},
    }

    assert decider(entree, "C:\\Users\\X\\Projet") is None


def test_un_chemin_relatif_est_rattache_a_la_racine() -> None:
    entree = ecriture("dev-metier", "x")
    entree["tool_input"] = {"file_path": "backend/app/etapes/domain/x.py"}

    assert decider(entree, RACINE) is None


@pytest.mark.parametrize("agent", AGENTS_ECRIVAINS)
def test_un_agent_ecrivain_ne_peut_pas_ecrire_hors_du_depot(agent: str) -> None:
    entree = {
        "agent_type": agent,
        "tool_name": "Write",
        "tool_input": {"file_path": "C:/Autre/x.py"},
    }

    assert decider(entree, RACINE) is not None


def test_un_chemin_qui_remonte_au_dessus_de_la_racine_est_hors_du_depot() -> None:
    entree = ecriture("dev-socle", "deploy/../../Autre/x.yaml")

    assert decider(entree, RACINE) is not None


@pytest.mark.parametrize(
    ("chemin", "attendu"),
    [
        ("C:/Users/X/Projet/a/b.py", "a/b.py"),
        ("c:\\users\\x\\projet\\A\\B.py", "a/b.py"),
        ("/c/Users/X/Projet/a/b.py", "a/b.py"),
        ("C:/Users/X/Projet", "."),
        ("C:/Users/X/Projet/a/../b.py", "b.py"),
        ("C:/Users/X/ProjetVoisin/a.py", None),
        ("C:/Users/X/Projet/../a.py", None),
        ("D:/Projet/a.py", None),
        ("/d/Users/X/Projet/a.py", None),
    ],
)
def test_chemin_relatif_compare_comme_du_texte(chemin: str, attendu: str | None) -> None:
    assert chemin_relatif(chemin, RACINE) == attendu


def test_chemin_relatif_accepte_une_racine_posix_et_une_racine_finie_par_un_separateur() -> None:
    assert chemin_relatif("/home/x/depot/a.py", "/home/x/depot/") == "a.py"


def test_sous_linux_un_chemin_en_slash_lettre_nest_pas_converti() -> None:
    assert chemin_relatif("/c/depot/a.py", "/c/depot") == "a.py"
    assert chemin_relatif("/c/x.py", "/home/x/depot") is None


@pytest.mark.parametrize("agent", SANS_ECRITURE)
@pytest.mark.parametrize("chemin", [f"{RACINE}/docs/x.md", "C:/Autre/x.md"])
def test_un_agent_sans_droit_decriture_est_toujours_refuse(agent: str, chemin: str) -> None:
    entree = {"agent_type": agent, "tool_name": "Edit", "tool_input": {"file_path": chemin}}

    assert decider(entree, RACINE) is not None


def test_un_agent_inconnu_est_refuse_dans_le_depot() -> None:
    assert decider(ecriture("general-purpose", "docs/x.md"), RACINE) is not None


def test_un_agent_inconnu_est_accepte_hors_du_depot() -> None:
    entree = {
        "agent_type": "general-purpose",
        "tool_name": "Write",
        "tool_input": {"file_path": "C:/Temp/scratch.md"},
    }

    assert decider(entree, RACINE) is None


@pytest.mark.parametrize("agent_type", [None, ""])
def test_la_session_principale_ecrit_et_commite_librement(agent_type: str | None) -> None:
    ecrire = {"tool_name": "Write", "tool_input": {"file_path": f"{RACINE}/.claude/settings.json"}}
    commiter = {"tool_name": "Bash", "tool_input": {"command": "git commit -m x"}}

    assert decider({"agent_type": agent_type, **ecrire}, RACINE) is None
    assert decider({"agent_type": agent_type, **commiter}, RACINE) is None


def test_un_agent_absent_de_lentree_est_la_session_principale() -> None:
    assert decider({"tool_name": "Bash", "tool_input": {"command": "git push"}}, RACINE) is None


@pytest.mark.parametrize("outil", ["Read", "Grep", "Glob", "WebFetch", ""])
def test_un_outil_inconnu_est_accepte(outil: str) -> None:
    entree = {"agent_type": "dev-metier", "tool_name": outil, "tool_input": {"file_path": "C:/x"}}

    assert decider(entree, RACINE) is None
