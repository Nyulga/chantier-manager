# Recettes du projet chantier-manager. Elles fonctionnent sous Windows (PowerShell) et sous Linux.
# Prérequis : just, uv, Node 24 et pnpm. Liste des recettes : `just --list`.

set windows-shell := ["powershell.exe", "-NoLogo", "-NoProfile", "-Command"]

# Affiche la liste des recettes.
defaut:
    @just --list

# Installe les dépendances du backend et du frontend, aux versions verrouillées.
installer:
    cd backend; uv sync --locked
    cd frontend; pnpm install --frozen-lockfile

# Lance l'API (port 8000) et le frontend (port 5173, avec son proxy /api) pour le développement.
[parallel]
lancer: _lancer-api _lancer-web

[working-directory: 'backend']
_lancer-api:
    uv run uvicorn app.main:creer_application --factory --reload --port 8000

[working-directory: 'frontend']
_lancer-web:
    pnpm dev

# Lance toutes les vérifications du projet : c'est la porte d'entrée de la CI.
verifier: verifier-back verifier-front

# Vérifications du backend : style, typage, architecture, tailles, sécurité, tests et couverture.
[working-directory: 'backend']
verifier-back:
    uv run ruff check .
    uv run ruff format --check .
    uv run mypy
    uv run lint-imports
    uv run python tools/verifier_tailles.py
    uv run bandit -c pyproject.toml -r app tools -q
    uv run pytest
    uv run coverage report --include="*/domain/*,*/application/*" --fail-under=100

# Vérifications du frontend : lint, typage, format, tests avec couverture et construction.
[working-directory: 'frontend']
verifier-front:
    pnpm lint
    pnpm typecheck
    pnpm format:check
    pnpm test
    pnpm build

# Lance un test backend ciblé, sans seuil de couverture. Exemple : just test-back -k avancement
[working-directory: 'backend']
test-back *args:
    uv run pytest --no-cov {{args}}

# Lance un test frontend ciblé, sans couverture. Exemple : just test-front useEtatApi
[working-directory: 'frontend']
test-front *args:
    pnpm exec vitest run {{args}}

# Lance les tests de bout en bout (Playwright, Chromium) sur le site construit.
[working-directory: 'frontend']
e2e:
    pnpm e2e

# Régénère les types TypeScript de l'API à partir du schéma OpenAPI du backend.
client:
    cd backend; uv run python -m tools.exporter_openapi ../frontend/openapi.json
    cd frontend; pnpm exec openapi-typescript openapi.json -o src/api/schema.d.ts
