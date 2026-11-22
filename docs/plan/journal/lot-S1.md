# Journal du lot S1 – Socle allégé

**Issue** : #10 · **Statut** : terminé le 2026-11-22 · **Plage** : de `308983c` à la clôture de S1

**Écart de process** : pour tenir le délai de mise en ligne, les étapes de S1 et de S2 ont été menées en parallèle sur `dev`. L'historique a ensuite été réordonné (S1, puis S2) pour livrer une PR par lot, à la demande du propriétaire ; l'ancien historique est conservé dans la branche `sauvegarde/dev-avant-demelage`. Les identifiants de commit cités ici sont ceux d'avant ce réordonnancement.

## Étape 1 – Socle backend et garde-fous

- **Agent** : `dev-socle` (Sonnet, élevé).
- **Livré** :
  - FastAPI, avec une fabrique `creer_application()` et `GET /api/health` ;
  - ruff (règles `D`, `C901`, `PLR`), mypy strict, bandit, pytest-cov ;
  - 8 contrats import-linter ;
  - le script `tools/verifier_tailles.py`.
- **Tests** :
  - `tests/integration/shared/test_sante.py` (3 tests) ;
  - `tests/unitaires/outils/test_verifier_tailles.py` (13 tests) ;
  - `tests/architecture/test_contrats_importlinter.py` (24 tests : chaque contrat échoue sur une violation volontaire) ;
  - `test_limites_taille.py`.
- **Rouge** : imports introuvables, puis violations volontaires détectées (contrats cassés, fichier ou fonction trop longs).
- **Vert** : `43 passed`, couverture de 100 %, 8 contrats respectés.
- **Commit** : `1f151a8`.

## Étape 2 – Socle frontend, thème Balise et garde-fous ESLint

- **Agent** : `dev-socle` (Sonnet, élevé).
- **Livré** :
  - Vite, React et TypeScript strict ;
  - 24 garde-fous ESLint : couches, éléments HTML et `className` interdits hors `ui`, valeurs Tailwind arbitraires, `fetch` hors `api`, cycles, complexité et tailles ;
  - le thème Balise, avec ses tokens seuls et les polices auto-hébergées ;
  - les composants `Page`, `Titre` et `Texte`.
- **Tests** :
  - `tests/garde-fous/garde-fous.test.ts` (30 tests, sur un mini-projet de fixtures : chaque violation déclenche la règle attendue) ;
  - `tests/theme/balise.test.ts` ;
  - les e2e `accueil.spec.ts` à 360 et 1280 px.
- **Rouge** : `Failed to resolve import "./PageAccueil"`. Quand la configuration est affaiblie, le test des garde-fous passe à 9 échecs sur 30.
- **Vert** : 100 tests, couverture de 100 %, 12 tests e2e.
- **Commit** : `32f7d87`.

## Étape 3 – justfile, client OpenAPI, CI et fichiers de déploiement

- **Agent** : `dev-socle` (Sonnet, élevé).
- **Livré** :
  - le `justfile` (`installer`, `lancer`, `verifier`, `test-back`, `test-front`, `e2e`, `client`) ;
  - `.gitattributes` ;
  - l'export OpenAPI et `schema.d.ts` généré ;
  - la CI GitHub (jobs backend et frontend) ;
  - `deploy/` : images non root, compose de production sans port publié, bloc Caddy.
- **Rouge** : `ModuleNotFoundError: No module named 'tools.exporter_openapi'` et `Failed to resolve import "./useEtatApi"`.
- **Vert** : `6 passed` pour l'exporteur et 104 tests pour le frontend. Le test Docker local est vert : `/api/health` répond 200 et le repli SPA fonctionne.
- **Commits** :
  - `eb5d2ca` ;
  - `2c1f3b7` : version existante de `setup-uv`, car la première CI échouait sur `setup-uv@v10` introuvable.

## Vérifications

- **securite** (Opus) : aucun constat bloquant. Quatre corrections ont été faites avant la mise en ligne, dans le commit `0fdb589` :
  - la CSP, `Permissions-Policy` et COOP ;
  - la limite de 64 Ko sur le corps des requêtes ;
  - la documentation de l'API masquée en production ;
  - les sauvegardes hors du dépôt, et un `.gitignore` qui couvre les bases et les dumps.

  Le reste est passé en issues (label `securite`) : #13 à #16.
- **revue** (Opus) : aucun bug bloquant. La remarque sur les fichiers de déploiement non commités est réglée par `0fdb589`.
- **conformite** (Sonnet) : conforme. Les réserves sont passées en issues (label `relecture`) : #20 (contrats de ports complets) et #21 (jscpd et pre-commit).
- **CI** : verte sur `dev` au commit de clôture de S1.
