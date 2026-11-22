# Lot 01 – Socle

**Dépend de** : — · **Statut** : à faire

## Objectif
Disposer d'un dépôt outillé où un squelette backend et frontend démarre, avec une CI qui fait respecter dès le premier jour toutes les exigences de qualité et de sécurité.

## Contenu
- **Arborescence**
  - `backend/` : projet uv, avec un package `app/` contenant les modules vides `auth`, `chantiers`, `etapes`, `documents`, `rgpd` et `shared`, chacun découpé en `domain`, `application`, `infrastructure` et `api`.
  - `backend/app/composition/` et `backend/app/cli/` vides ; `backend/tests/` découpé en `unitaires/`, `contrats/`, `integration/` et `architecture/` ; `backend/migrations/` (Alembic).
  - `frontend/` : projet Vite, React et TypeScript géré avec pnpm, avec `src/app/`, `src/api/`, `src/ui/` et `src/features/` (voir `.claude/rules/05-frontend.md`).
- **Qualité backend** : ruff (lint et formatage), mypy `--strict`, bandit, pytest avec pytest-cov (seuils configurés), hypothesis, mutmut configuré.
- **Contrats d'architecture** (ADR 0005) :
  - backend : import-linter, avec les couches par module, l'indépendance des modules, `shared` qui n'importe aucun module métier, et SQLAlchemy et psycopg réservés à l'`infrastructure` ;
  - frontend : ESLint, avec `eslint-plugin-boundaries`, `no-restricted-imports`, `import/no-cycle`, `react/forbid-elements` et `react/forbid-dom-props` hors de `src/ui`, et les valeurs Tailwind arbitraires interdites ;
  - un test prouve, pour chaque type de contrat, qu'une violation fait échouer le contrôle.
- **Garde-fous anti-spaghetti** (règle 00, §4) :
  - ruff : `C901`, `PLR0911`, `PLR0912`, `PLR0913`, `PLR0915`, `PLR2004`, et les docstrings obligatoires des modules et des classes publiques (`D100`, `D101`, `D104`) ;
  - ESLint : `complexity`, `max-lines`, `max-lines-per-function`, `max-depth`, `max-params`, `max-nested-callbacks` ;
  - un script qui mesure les lignes par fichier et par fonction en Python ;
  - jscpd (≤ 2 %) ;
  - un contrôle CI qui refuse `noqa`, `type: ignore`, `eslint-disable`, `@ts-ignore` et `pragma: no cover` non approuvés.
- **Thème Tailwind** : les tokens de `docs/design-system.md`, et les premiers composants `src/ui` nécessaires à la page d'accueil.
- **Qualité frontend** : TypeScript strict (`noUncheckedIndexedAccess`, `exactOptionalPropertyTypes`), ESLint strict, Prettier, Vitest, Testing Library, Playwright.
- **Client API généré** : script openapi-typescript, et la CI vérifie que le client généré est à jour.
- **Squelette fonctionnel** : `GET /api/health` côté backend ; côté frontend, une page d'accueil en français qui appelle `/api/health` via le client généré.
- **Développement local** : `docker-compose.dev.yml` (PostgreSQL, ClamAV, Mailpit), `.env.example`, et un `justfile` (installer, lancer, tester, lint, générer le client).
- **pre-commit** : ruff, mypy, ESLint, Prettier, gitleaks.
- **CI GitHub Actions** : jobs backend, frontend, e2e, mutation (Linux) et sécurité (pip-audit, pnpm audit, bandit, gitleaks, CodeQL, Trivy), plus Dependabot.
- **Protection de `main`** : ajout des jobs de la CI comme checks obligatoires.
- **`CLAUDE.md`** : ajout des commandes réelles, y compris celle qui lance un seul test (backend et frontend).

## Critères d'acceptation
- [ ] `just` installe et lance le backend et le frontend en local ; la page d'accueil affiche l'état renvoyé par `/api/health`.
- [ ] La CI est verte sur `dev`, et chaque job échoue bien sur une erreur volontaire (vérifié une fois, puis annulé).
- [ ] Une importation interdite (par exemple `domain` qui importe `sqlalchemy`) fait échouer import-linter.
- [ ] Une page qui utilise un `<button>` brut ou appelle `src/api` directement fait échouer ESLint ; une fonction trop complexe ou trop longue fait échouer le lint.
- [ ] Les checks obligatoires sont actifs sur `main`.
- [ ] Couvre en partie `intent.md` §5.2 et §5.3 (l'outillage).

## Hors lot
Aucune logique métier, aucune table en base.
