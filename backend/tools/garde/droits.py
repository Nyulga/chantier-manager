"""Droits d'écriture des sous-agents (outils Edit et Write), couche par couche."""

from collections.abc import Mapping
from pathlib import Path, PurePosixPath

from tools.garde.agents import AGENTS_SANS_ECRITURE
from tools.garde.chemins import chemin_relatif, est_suspect, normaliser
from tools.garde.refus import refus

# Droits d'écriture de chaque sous-agent, en motifs relatifs à la racine du dépôt. Ils reprennent le
# découpage en couches des règles 01 à 07 et l'outillage de la règle 09. Un agent absent de cette
# table n'écrit nulle part dans le dépôt.
DROITS_ECRITURE: Mapping[str, tuple[str, ...]] = {
    "dev-metier": (
        "backend/app/*/domain/**",
        "backend/app/*/application/**",
        "backend/app/*/infrastructure/memoire/**",
        "backend/app/shared/infrastructure/*_memoire.py",
        "backend/tests/domain/**",
        "backend/tests/application/**",
        "backend/tests/fabriques/**",
        "backend/tests/infrastructure/*/test_*memoire*.py",
    ),
    "dev-donnees": (
        "backend/app/*/infrastructure/**",
        "backend/app/composition/**",
        "backend/app/cli/**",
        "backend/app/main.py",
        "backend/alembic.ini",
        "backend/migrations/**",
        "backend/tests/infrastructure/**",
        "backend/tests/contrats/**",
        "backend/tests/migrations/**",
        "backend/tests/integration/**",
        "backend/tests/composition/**",
        "backend/tests/conftest.py",
    ),
    "dev-api": (
        "backend/app/*/api/**",
        "backend/tests/api/**",
        "backend/tests/integration/**",
        "frontend/src/api/schema.d.ts",
        "frontend/openapi.json",
    ),
    "dev-frontend": (
        "frontend/src/**",
        "frontend/e2e/**",
        "frontend/tests/**",
        "frontend/public/**",
        "frontend/index.html",
    ),
    "dev-socle": (
        "deploy/**",
        ".github/**",
        "justfile",
        ".pre-commit-config.yaml",
        ".editorconfig",
        ".gitattributes",
        ".gitignore",
        "backend/.gitignore",
        "backend/tools/**",
        "backend/tests/outils/**",
        "backend/tests/architecture/**",
        "backend/pyproject.toml",
        "backend/uv.lock",
        "frontend/.gitignore",
        "frontend/.npmrc",
        "frontend/.prettierignore",
        "frontend/.prettierrc.json",
        "frontend/package.json",
        "frontend/pnpm-lock.yaml",
        "frontend/eslint/**",
        "frontend/eslint.config.js",
        "frontend/tsconfig*.json",
        "frontend/vite.config.ts",
        "frontend/vitest.setup.ts",
        "frontend/playwright.config.ts",
        "frontend/tests/garde-fous/**",
    ),
}

# Exceptions aux droits de `dev-frontend` : le client généré n'est jamais écrit à la main
# (ADR 0013), et les tests des garde-fous appartiennent à `dev-socle`, comme le reste de
# l'outillage (absent de la liste de `dev-frontend`), pour qu'un agent ne puisse pas assouplir les
# règles qui le contrôlent.
EXCLUSIONS_ECRITURE: Mapping[str, tuple[str, ...]] = {
    "dev-frontend": ("frontend/src/api/schema.d.ts", "frontend/tests/garde-fous/**"),
}

# Fichiers de la garde, protégés pour tous les sous-agents avant toute autre règle : un agent ne
# doit pas pouvoir élargir ses propres droits. `backend/tools/__init__.py` est exécuté à chaque
# chargement de la garde. La configuration de Claude Code est protégée à part (`_est_protege`).
FICHIERS_PROTEGES = (
    "backend/tools/__init__.py",
    "backend/tools/garde_agents.py",
    "backend/tools/garde/**",
    "backend/tests/outils/*garde_agents*.py",
)


def _correspond(relatif: str, motifs: tuple[str, ...]) -> bool:
    return any(PurePosixPath(relatif).full_match(motif.casefold()) for motif in motifs)


def _est_protege(chemin: str, relatif: str | None) -> bool:
    # `.claude/` et `.claude.json` sont protégés partout, dans le dépôt comme dans le dossier
    # personnel : c'est là que vivent les hooks et les permissions.
    composants = normaliser(chemin).split("/")
    if ".claude" in composants or composants[-1] == ".claude.json":
        return True
    return relatif is not None and _correspond(relatif, FICHIERS_PROTEGES)


def _raison_protection(agent: str, chemin: str, relatif: str | None) -> str | None:
    """Refus qui valent pour tous les sous-agents, quels que soient leurs droits."""
    if est_suspect(chemin):
        return refus(agent, f"d'écrire dans « {chemin} » : cette forme de chemin est inconnue")
    if _est_protege(chemin, relatif):
        return refus(agent, f"de modifier « {relatif or chemin} » : ce fichier est protégé")
    return None


def raison_ecriture(agent: str, chemin: str, racine: str | Path) -> str | None:
    """Dit pourquoi l'écriture est refusée, ou renvoie `None` si elle est permise."""
    relatif = chemin_relatif(chemin, racine)
    protection = _raison_protection(agent, chemin, relatif)
    if protection is not None:
        return protection
    if agent in AGENTS_SANS_ECRITURE:
        return refus(agent, "d'écrire des fichiers")
    if relatif is None:
        # Hors du dépôt, seuls les agents sans table de droits (un agent généraliste) écrivent.
        return refus(agent, "d'écrire hors du dépôt") if agent in DROITS_ECRITURE else None
    permis = _correspond(relatif, DROITS_ECRITURE.get(agent, ()))
    exclu = _correspond(relatif, EXCLUSIONS_ECRITURE.get(agent, ()))
    return None if permis and not exclu else refus(agent, f"d'écrire dans « {relatif} »")
