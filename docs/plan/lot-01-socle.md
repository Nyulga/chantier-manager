# Lot 01 – Socle

**Dépend de** : — · **Statut** : à faire

## Objectif
Disposer d'un dépôt outillé où un squelette backend et frontend démarre, avec une CI qui fait respecter dès le premier jour toutes les exigences de qualité et de sécurité.

## Contenu
- **Arborescence**
  - `backend/` : projet uv, avec un package `app/` contenant les modules vides `auth`, `chantiers`, `etapes`, `documents`, `rgpd` et `shared`, chacun découpé en `domain`, `application`, `infrastructure` et `api`.
  - `frontend/` : projet Vite, React et TypeScript géré avec pnpm, avec `src/features/` et `src/shared/`.
- **Qualité backend** : ruff (lint et formatage), mypy `--strict`, bandit, pytest avec pytest-cov (seuils configurés), hypothesis, mutmut configuré.
- **Contrats d'architecture** : configuration import-linter (couches par module et indépendance des modules), avec un test qui prouve qu'une violation fait échouer le contrôle.
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
- [ ] Les checks obligatoires sont actifs sur `main`.
- [ ] Couvre en partie `intent.md` §5.2 et §5.3 (l'outillage).

## Hors lot
Aucune logique métier, aucune table en base.
