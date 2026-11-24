# Lot 01 – Socle

**Dépend de** : — · **Statut** : à faire · **Issue** : #1 · **Références** : [ADR 0001](../decisions/0001-monolithe-modulaire-hexagonal.md), [ADR 0005](../decisions/0005-design-patterns-et-garde-fous.md)

## Objectif
Disposer d'un dépôt outillé où un squelette backend et frontend démarre, avec une CI qui fait respecter **dès le premier jour** toutes les exigences de qualité, d'architecture et de sécurité.

## Prérequis et points à trancher au démarrage
- **Poste de l'utilisateur** : Docker Desktop (avec WSL 2) installé et démarré, à installer par l'utilisateur. uv et just, installés avec son accord. Le coordinateur vérifie leur présence avant toute étape.
- **Accord de l'utilisateur** requis pour modifier la protection de `main` (étape 6).

## Étapes
| # | Agent (modèle, effort) | Contenu | Règles |
|---|---|---|---|
| 1 | `dev-socle` (Sonnet, élevé) | **Backend** : projet uv, avec le package `app/` et les modules vides `auth`, `chantiers`, `etapes`, `documents`, `rgpd` et `shared`, chacun découpé en `domain`, `application`, `infrastructure` et `api`. Dossiers vides `app/composition/` et `app/cli/`. `backend/tests/` découpé par couche (`domain/`, `application/`, `infrastructure/`, `api/`, `composition/`), puis `contrats/`, `integration/`, `migrations/` et `architecture/`. `backend/migrations/` (Alembic, vide). Outils qualité : ruff (lint et format, `C901`, `PLR0911`, `PLR0912`, `PLR0913`, `PLR0915`, `PLR2004`, docstrings `D100`, `D101` et `D104`), mypy `--strict`, bandit, pytest et pytest-cov (seuils configurés), hypothesis, mutmut. Script de mesure des lignes par fichier et par fonction. **Contrats import-linter** : couches par module, indépendance des modules, `shared` qui n'importe aucun module métier, SQLAlchemy et psycopg réservés à l'`infrastructure`. | 00, 06, 07 |
| 2 | `dev-socle` (Sonnet, élevé) | **Frontend** : projet Vite, React et TypeScript (pnpm), avec `src/app/`, `src/api/`, `src/ui/` et `src/features/`. TypeScript strict (`noUncheckedIndexedAccess`, `exactOptionalPropertyTypes`). ESLint strict : `eslint-plugin-boundaries`, `no-restricted-imports`, `import/no-cycle`, et hors de `src/ui`, `react/forbid-elements` et `react/forbid-dom-props` ; valeurs Tailwind arbitraires interdites ; limites `complexity`, `max-lines`, `max-lines-per-function`, `max-depth`, `max-params` et `max-nested-callbacks`. Prettier, Vitest, Testing Library, axe, MSW, Playwright. **Thème Tailwind** reprenant tous les tokens de `docs/design-system.md` (clair et sombre). Polices Archivo et IBM Plex Mono **auto-hébergées**. | 00, 05 |
| 3 | `dev-socle` (Sonnet, élevé) | **Squelette de bout en bout** : `GET /api/health`, schéma OpenAPI, client généré (openapi-typescript et openapi-fetch) dans `src/api/`, et page d'accueil en français qui affiche l'état de l'API. La CI vérifie que le client généré est à jour. `justfile` avec les recettes `installer`, `lancer`, `verifier`, `test-back`, `test-front`, `e2e` et `client`, qui fonctionnent sous Windows et sous Linux. | 00, 04, 05 |
| 4 | `dev-socle` (Sonnet, élevé) | **Développement local** : `docker-compose.dev.yml` (PostgreSQL, ClamAV, Mailpit), `.env.example` avec des valeurs fictives. **pre-commit** : ruff, mypy, ESLint, Prettier, gitleaks, jscpd (≤ 2 %), et un contrôle qui refuse `noqa`, `type: ignore`, `eslint-disable`, `@ts-ignore`, `@ts-expect-error` et `pragma: no cover` non approuvés. | 00 |
| 5 | `dev-socle` (Sonnet, élevé) | **CI GitHub Actions** : jobs `backend`, `frontend`, `e2e`, `mutation` (Linux) et `securite` (pip-audit, pnpm audit, bandit, gitleaks, CodeQL, Trivy), plus Dependabot. Pour **chaque garde-fou**, la preuve qu'il échoue sur une violation volontaire, puis repasse au vert une fois la violation retirée. Les preuves durables sont des tests dans `backend/tests/architecture/`. | 00, 07 |
| 6 | Coordinateur | Avec l'accord de l'utilisateur : ajout des jobs de la CI comme **checks obligatoires** sur `main`. Ajout des commandes réelles dans `CLAUDE.md` (« État du projet »), y compris celle qui lance un seul test. | — |

## Composants `ui` introduits
`Page`, `Titre` et `Texte`, juste ce qu'il faut pour la page d'accueil. Chacun a son test d'accessibilité.

## Critères d'acceptation → tests
| Critère | Preuve | Couche |
|---|---|---|
| `just installer` puis `just lancer` démarrent le backend et le frontend ; la page d'accueil affiche l'état renvoyé par `/api/health` | Test d'intégration de `/api/health`, test Vitest de la page, test Playwright de la page d'accueil | API, frontend |
| Une importation interdite (`domain` qui importe `sqlalchemy`, `api` qui importe `infrastructure`, `shared` qui importe `chantiers`) fait échouer import-linter | `tests/architecture/test_contrats_import_linter.py` (violation simulée) | Architecture |
| Une page qui utilise un `<button>` brut, une prop `className`, ou qui appelle `src/api` directement, fait échouer ESLint | Test des règles ESLint sur des fichiers de violation | Architecture frontend |
| Une fonction trop longue ou trop complexe, ou un fichier trop long, fait échouer le lint | `tests/architecture/test_limites_de_taille.py`, et un test sur la configuration ESLint | Architecture |
| Un module ou une classe publique sans docstring fait échouer ruff | Violation volontaire, montrée dans le journal du lot | Architecture |
| La CI est verte sur `dev`, et chaque job échoue bien sur une erreur volontaire | Liens vers les exécutions rouge et verte, consignés dans le journal | CI |
| Les checks obligatoires sont actifs sur `main` | `gh api repos/Nyulga/chantier-manager/branches/main/protection` | GitHub |
| L'outillage couvre en partie `intent.md` §5.2 et §5.3 | Tableau du journal | — |

## Hors lot
Aucune logique métier, aucune table en base.
