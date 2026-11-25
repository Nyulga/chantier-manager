# Journal du lot S7 – Garde-fous des agents et du client généré

**Issue** : #71 (sous-issues #46 et #43) · **Statut** : terminé le 2026-11-25 · **Plage** : `6238860..` (clôture)

Pendant le lot S6, un comptage SQL a failli être confié à `dev-metier`, hors de sa couche. Le propriétaire veut que ce genre d'écart soit refusé automatiquement (#46). Le lot ajoute aussi le contrôle du client TypeScript généré (#43). Les choix sont consignés dans l'ADR 0017.

## Décisions du propriétaire

Plan validé le 2026-11-25 (« lance le lot 7 »), avec les cinq recommandations du coordinateur :
- `dev-metier` peut écrire les implémentations en mémoire ;
- les vérificateurs (`revue`, `conformite`, `securite`) n'ont pas droit à `rm`, `mv`, `cp`, `tee` ni `sed -i` ; `pentest` et `backlog` n'ont que la garde git ;
- un sous-agent inconnu a la garde git et n'écrit pas dans le dépôt ;
- seul le coordinateur corrige la garde, avec l'accord du propriétaire ;
- un ADR (0017) consigne ces choix.

Après la première vérification (« A oui B oui C oui ») :
- **A** : le coordinateur corrige lui-même la garde, en TDD, puisqu'aucun sous-agent ne peut la modifier ;
- **B** : les règles de permission de `.claude/settings.json` sont resserrées ;
- **C** : la lecture du critère de #71 est conservée : `dev-metier` écrit dans `shared/domain`, `shared/application` et les implémentations en mémoire, et il est refusé dans le reste de `shared/infrastructure`.

## Hors lot, pendant le lot (`chore`)

- **Règles de permission** du projet (`49ab366`, `e404bd3`, `5ad7c35`, `680e62f`, `52ec56e`) : `allow` pour les commandes de vérification et de lecture git, `ask` pour la création de PR et `ssh`/`scp`, `deny` pour la fusion de PR, tout push vers `main` ou forcé, la lecture des secrets (`.env`, `.env.local`, `~/.claude.json`, `~/.ssh`). Testées une par une (refus de `git push --dry-run origin main`, de `dev:main`, de `--force`, de `git diff --no-index`, de la lecture d'un faux `.env` ; demande pour `ssh -V`).
- **Python** mis à jour de 3.13 vers 3.13.17 sur le poste (`python --version` → `Python 3.13.17`).
- **Hook ESLint** après chaque modification du frontend (`e45ca4e`), demandé par le propriétaire.

## Étape 1 – Script de garde (`dev-socle`, Sonnet, effort élevé) · `c23187f`

Script `backend/tools/garde_agents.py`, en bibliothèque standard, qui lit l'entrée JSON du hook `PreToolUse` et refuse :
- une écriture (`Edit`, `Write`) d'un agent développeur hors des dossiers de sa couche ;
- les commandes git qui modifient le dépôt, pour tous les sous-agents ;
- les commandes d'écriture pour les vérificateurs.

La session principale (sans `agent_type`) n'est jamais concernée.

**Rouge** : `pytest tests/outils/test_garde_agents.py` échoue sur `ModuleNotFoundError: No module named 'tools.garde_agents'`, pour la bonne raison.
**Vert** : 229 tests passés, couverture de `garde_agents.py` à 100 % (lignes et branches).

## Étape 2 – Hook branché pour tous les sous-agents (coordinateur) · `70b79f7`

Un seul hook de projet dans `.claude/settings.json`, sur `Edit|Write|Bash`, qui lance `python -I "$CLAUDE_PROJECT_DIR/backend/tools/garde_agents.py"`.

**Preuve réelle**, avec un vrai `dev-metier` (Haiku, effort faible) :
- écriture dans `backend/app/shared/infrastructure/` : refusée, le fichier n'existe pas ;
- écriture dans `backend/app/etapes/domain/` : acceptée (fichier supprimé ensuite) ;
- `git stash list` : refusé (faux positif assumé, issue #79).

## Étape 3 – Contrôle du client généré (`dev-socle`, Sonnet, effort élevé) · `24d6a8f`

Recette `just verifier-client`, ajoutée à `just verifier` et à la CI (job Frontend) : elle régénère le client dans un dossier temporaire et le compare au fichier commité, sans tenir compte des fins de ligne.

| | Action | Résultat |
|---|---|---|
| Rouge | description d'un champ de l'API modifiée sans `just client`, puis `just verifier-client` | code 1 : la ligne changée, puis « Le client généré n'est pas à jour : lance 'just client' et commite frontend/src/api/schema.d.ts. » |
| Vert | modification annulée, `just verifier-client` | code 0 : « Le client généré est à jour. » |

## Vérification, premier passage

| Vérificateur | Bloquant | Important | Mineur |
|---|---|---|---|
| `revue` (Opus, élevé) | 1 (`dev-api` sans droit sur ses tests d'intégration) | 6 | — |
| `conformite` (Sonnet, élevé) | 0 | 6 (dont le script de 299 lignes à découper) | — |
| `securite` (Opus, élevé) | 0 | 2 (la garde laissait passer en cas de panne ; règles `allow` trop larges) | 5 |

Les mineurs et les limites hors lot sont devenus les issues #77 à #82 (agent `backlog`, Sonnet, effort faible).

**Écart observé pendant le lot** : en testant sa recette, `dev-socle` a modifié puis restauré `frontend/src/api/schema.d.ts` par une commande du terminal, alors que ce fichier ne lui appartient pas. La garde ne voit que `Edit` et `Write` : c'est la limite assumée dans l'ADR 0017.

## Corrections

### Garde (coordinateur, TDD) · `a8ca581`

- table des droits complétée : tests d'intégration pour `dev-api`, tests mémoire pour `dev-metier` ; outillage du frontend (ESLint, TypeScript, Vite, dépendances, tests des garde-fous) réservé à `dev-socle`, client généré interdit à `dev-frontend` ;
- `.claude/` et `.claude.json` protégés partout, ainsi que la garde et ses tests ; formes de chemin trompeuses sous Windows refusées ; chemins Git Bash (`/c/...`) reconnus ;
- git en liste blanche de sous-commandes de lecture ; `gh pr checkout` et `gh pr merge` refusés ; options `--output` refusées ;
- lignes prolongées par `\`, PowerShell, `cmd`, `xargs`, `timeout`, `sudo` et `nice` analysés ;
- toute panne bloque un sous-agent (code 2), et le hook finit par `|| exit 2` ; messages en UTF-8 ;
- script découpé en paquet `backend/tools/garde/` ; test d'alignement entre la table des droits, les fiches d'agents et le hook.

**Rouge** : `just test-back tests/outils/ -q -p no:randomly` → `95 failed, 292 passed` (`assert None is not None` pour les refus attendus, `'protégé' in …`, `'forme de chemin'`, message en cp1252 au lieu d'UTF-8, `ModuleNotFoundError` attendu pour le nouveau paquet).
**Vert** : `387 passed` ; ruff, format et mypy sans remarque.

Essai du hook réel par l'entrée standard : session principale → code 0 ; `dev-metier` dans `shared/infrastructure` → `deny` ; `git pull` par `revue` → `deny`.

### Recette `client` (`dev-socle`, Sonnet, effort élevé) · `a670fb0`

Le chemin de sortie arrive en argument positionnel et n'est plus recopié dans le script : une valeur hostile reste un nom de fichier. L'export passe par `uv run --no-dev`. Preuve rouge refaite après la correction : code 1, puis code 0 après annulation ; `just client` sans argument réécrit le client à l'identique.

**`just verifier`** après les corrections : code 0, `1372 passed`, couverture backend 99,81 %, 8 contrats tenus, `488` tests frontend, « Le client généré est à jour. »

## Vérification, second passage

Limité aux corrections (`24d6a8f..e45ca4e`).

| Vérificateur | Bloquant | Important | Mineur |
|---|---|---|---|
| `revue` (Opus, élevé) | 0 | 1 (`dev-frontend` peut créer un fichier d'outillage absent des exclusions, par exemple un `vitest.config.ts` sans seuils) | 12 |
| `conformite` (Sonnet, élevé) | 0 | 2 (un test remplaçait notre propre fonction par un double ; noms des vérificateurs écrits à deux endroits) | 7 |
| `securite` (Opus, élevé) | 0 | 1 (arguments de `test-back` et `test-front` interprétés par le shell, recettes autorisées sans confirmation : issue #81) | 9 |

Les cinq constats du premier passage sont confirmés corrigés par `revue`, et I1 par `securite`.

## Corrections du second passage

### Garde (coordinateur, TDD) · `0178453`

- `dev-frontend` en liste blanche : `src`, `e2e`, `tests` (hors `garde-fous`), `public` et `index.html` ;
- `git -c`, `--config-env` et `git grep -O` refusés : ils font lancer un programme même par une commande de lecture ;
- `backend/tools/__init__.py`, chargé avec la garde, protégé ;
- noms des vérificateurs et des agents sans écriture définis une seule fois (`tools/garde/agents.py`), test d'alignement par ensembles, fiche sans `tools` comptée comme écrivant ;
- panne provoquée pour de vrai (pile d'appels réduite et commande imbriquée), sans double de notre propre code (règle 07) ;
- un test par comportement, commentaires complétés.

**Rouge** : d'abord `ModuleNotFoundError: No module named 'tools.garde.agents'` (3 fichiers de tests), puis, le module créé, `12 failed, 386 passed` : six écritures d'outillage par `dev-frontend` acceptées (`vitest.config.ts`, `.prettierrc`, `pnpm-workspace.yaml`, `.pnpmfile.cjs`, `.jscpd.json`, `node_modules`), et `backend/tools/__init__.py` non protégé pour six agents. Les tests de `git -c` et `grep -O` ont été vus en échec dans le même passage.
**Vert** : `406 passed` ; ruff, format, mypy et limites de taille sans remarque. Le cas « `git -c` seul accepté » est devenu « `git --version` accepté », puisque `-c` est désormais refusé.

### Recettes de test (`dev-socle`, Sonnet, effort élevé) · `b3fedbd`, ferme #81

Arguments passés en positionnels (`"$@"`), dans une recette à shebang, comme pour `client`.
- **Rouge** : `just test-back 'tests/outils/test_verifier_tailles.py; echo INJECTE'` lance les 13 tests puis affiche `INJECTE`, code 0 ; même chose pour `test-front`.
- **Vert** : pytest reçoit le texte comme un seul chemin (`file or directory not found`, code 4) ; `x$(echo INJECTE2)` n'est pas exécuté ; usages normaux intacts (`-k avancement` : 18 tests ; `just test-front chantiers` : 71 tests).

### Hook de lint (hors lot) · `3d79e8a`

Entrée lue en UTF-8 (sous Windows, un « ” » faisait sauter le lint en silence), seul le dossier `frontend/` du projet contrôlé, `--max-warnings 0` comme en CI. Essais : fichier fautif avec « ” » et « ← » → code 2 ; fichier correct → 0 ; `frontend` hors du projet → ignoré.

**`just verifier`** : code 0, `1391 passed`, couverture backend 99,81 %, 8 contrats tenus, `488` tests frontend, « Le client généré est à jour. »

### Constats mineurs en issues (agent `backlog`, Sonnet, effort faible)

#83 (`gh` : alias, options, `gh api`, `gh pr review` pour les vérificateurs), #84 (substitutions entre guillemets doubles), #85 (lanceurs et interpréteurs mal lus), #86 (le hook bloque aussi le coordinateur si le point d'entrée plante), #87 (`__init__.py` de module), #88 (découper `commandes.py`), #89 (trous de la liste `deny`, à modifier avec l'accord du propriétaire), #90 (empreinte de pnpm), #91 (lisibilité du `justfile`) ; faux positifs supplémentaires ajoutés à #79.

## Test d'intrusion

Non lancé : le lot ne touche ni l'API, ni le frontend, ni le déploiement (skill `lot`, §4.5). Il ne change que l'outillage des agents, la CI et le `justfile`.

## Clôture

- **Définition de « terminé »** :
  - CI verte sur `dev` (`3d79e8a`, https://github.com/Nyulga/chantier-manager/actions/runs/45630700205) ;
  - code relu deux fois par `revue`, `conformite` et `securite` ; aucun bloquant au second passage, les importants corrigés ;
  - couverture backend 99,81 % (100 % sur domain et application), frontend au-dessus de 90 % ; le score de mutation n'est pas encore mesuré (phase 2) ;
  - décisions dans l'ADR 0017 ; `CLAUDE.md`, règles 04 et 09, skill `lot`, fiches d'agents, `docs/plan/README.md` et `squelette.md` à jour.
- **Critères de #71** : un sous-agent qui écrit hors de sa couche est refusé (tests et preuve réelle avec `dev-metier`) ; une commande git qui modifie le dépôt est refusée aux sous-agents ; un schéma d'API modifié sans `just client` fait échouer `just verifier` et la CI.
- Aucun critère d'`intent.md` §5 n'est rattaché à ce lot : il protège la façon de développer.
- **Mise en ligne** : rien à déployer, le lot ne change pas l'application.
