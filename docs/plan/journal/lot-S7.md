# Journal du lot S7 – Garde-fous des agents et du client généré

**Issue** : #71 (sous-issues #46 et #43) · **Statut** : en cours de clôture · **Plage** : `6238860..`

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

_À compléter._
