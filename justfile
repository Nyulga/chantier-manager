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
verifier: verifier-back verifier-front doublons

# Vérifications du backend : style, typage, architecture, tailles, sécurité, tests et couverture.
[working-directory: 'backend']
verifier-back: && _couverture-back
    uv run ruff check .
    uv run ruff format --check .
    uv run mypy
    uv run lint-imports
    uv run python tools/verifier_tailles.py
    uv run bandit -c pyproject.toml -r app tools -q

# Tests du backend avec leurs seuils : 95 % partout (dans pyproject.toml), 100 % sur domain et application.
[working-directory: 'backend']
_couverture-back:
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

# Le seuil de 2 % (règle 00, §4) s'applique au code de production, Python et TypeScript, et aux
# tests Python (0,31 % aujourd'hui). `--fail-on-empty` empêche un contrôle de réussir sans rien analyser.
# Les tests TypeScript ont un seuil séparé, plus haut : ils répètent leur mise en place (rendu, serveur
# simulé) pour rester lisibles seuls, et mesurent 6,3 % aujourd'hui. Les 7 % interdisent seulement
# d'aggraver la situation ; le regroupement des aides de test (issue #32) doit permettre de le baisser.

# Mesure la duplication de code : 2 % au plus en production, un seuil séparé pour les tests TypeScript.
[working-directory: 'frontend']
doublons:
    pnpm exec jscpd ../backend/app --format python --threshold 2 --fail-on-empty --no-tips
    pnpm exec jscpd ../backend/tests ../backend/tools --format python --threshold 2 --fail-on-empty --no-tips
    pnpm exec jscpd src --format "typescript,tsx" --ignore "**/*.test.ts,**/*.test.tsx,**/schema.d.ts" --threshold 2 --fail-on-empty --no-tips
    pnpm exec jscpd src --format "typescript,tsx" --pattern "**/*.test.{ts,tsx}" --threshold 7 --fail-on-empty --no-tips

# pre-commit est installé comme outil uv, à sa version exacte : le script de hook pointe alors vers un
# environnement durable (un `uvx` éphémère le laisserait pointer dans le vide). Pour passer un hook une
# fois : `SKIP=nom-du-hook git commit` (sous PowerShell : `$env:SKIP='nom-du-hook'`, puis `git commit`).

# Installe les hooks git : les contrôles rapides au commit, les tests au push (.pre-commit-config.yaml).
hooks:
    uv tool install pre-commit==4.7.0
    uv tool run --from pre-commit==4.7.0 pre-commit install

# Le dépôt est en LF (.gitattributes), mais des fichiers déjà présents avant cette règle sont restés en CRLF
# dans la copie de travail : ruff format et Prettier les refusent. `git checkout-index` les réécrit depuis
# l'index. La première ligne échoue, sans rien modifier, s'il reste des modifications non indexées, car
# elles seraient écrasées : indexe-les d'abord. Les fichiers non suivis ne sont pas touchés.

# Réécrit en LF les fichiers suivis restés en CRLF dans la copie de travail (Windows).
normaliser-fins-de-ligne:
    git diff --quiet
    git checkout-index --all --force

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

# Hooks pre-commit du frontend. Les fichiers arrivent depuis la racine du dépôt (`frontend/src/...`) :
# on retire le préfixe, car les outils tournent dans `frontend/`.
[working-directory: 'frontend']
_hook-prettier *fichiers:
    pnpm exec prettier --check --ignore-unknown {{replace(fichiers, "frontend/", "")}}

[working-directory: 'frontend']
_hook-eslint *fichiers:
    pnpm exec eslint --max-warnings 0 --no-warn-ignored {{replace(fichiers, "frontend/", "")}}
