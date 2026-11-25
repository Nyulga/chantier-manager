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
verifier: verifier-back verifier-front verifier-client doublons

# Vérifications du backend : style, typage, architecture, tailles, désactivations de règles, sécurité, tests et couverture.
[working-directory: 'backend']
verifier-back: && _couverture-back
    uv run ruff check .
    uv run ruff format --check .
    uv run mypy
    uv run lint-imports
    uv run python tools/verifier_tailles.py
    uv run python -m tools.verifier_desactivations
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
# tests Python. `--fail-on-empty` empêche un contrôle de réussir sans rien analyser.
# Taux mesurés (avant les corrections du lot S5) : backend `app` 0 %, tests Python 0,23 %,
# TypeScript de production 1,11 % et tests TypeScript 5,60 %.
# Les tests TypeScript ont un seuil séparé, plus haut (6 %) : ils répètent leur mise en place (rendu,
# serveur simulé) pour rester lisibles seuls. C'est une dérogation accordée par le propriétaire au lot S5,
# règle 00 §4. Le regroupement des aides de test (issue #32) doit permettre de la réduire.

# Mesure la duplication de code : 2 % au plus en production, un seuil séparé pour les tests TypeScript.
[working-directory: 'frontend']
doublons:
    pnpm exec jscpd ../backend/app --format python --threshold 2 --fail-on-empty --no-tips
    pnpm exec jscpd ../backend/tests ../backend/tools --format python --threshold 2 --fail-on-empty --no-tips
    pnpm exec jscpd src --format "typescript,tsx" --ignore "**/*.test.ts,**/*.test.tsx,**/schema.d.ts" --threshold 2 --fail-on-empty --no-tips
    pnpm exec jscpd src --format "typescript,tsx" --pattern "**/*.test.{ts,tsx}" --threshold 6 --fail-on-empty --no-tips

# pre-commit est installé comme outil uv, à sa version exacte : le script de hook pointe alors vers un
# environnement durable (un `uvx` éphémère le laisserait pointer dans le vide). Pour passer un hook une
# fois : `SKIP=nom-du-hook git commit` (sous PowerShell : `$env:SKIP='nom-du-hook'`, puis `git commit`).

# Installe les hooks git : les contrôles rapides au commit, les tests au push (.pre-commit-config.yaml).
hooks:
    uv tool install pre-commit==4.7.0
    uv tool run --from pre-commit==4.7.0 pre-commit install

# Le dépôt est en LF (.gitattributes), mais des fichiers déjà présents avant cette règle sont restés en CRLF
# dans la copie de travail : ruff format et Prettier les refusent. `git checkout-index --force` ne suffit
# pas : il saute tout fichier dont la taille et la date correspondent à l'entrée de l'index, et l'index a
# enregistré celles du fichier CRLF lors de son extraction ou d'un `git add`. La recette supprime donc
# d'abord les fichiers concernés (ceux que `git ls-files --eol` donne en `w/crlf` ou `w/mixed`), puis les
# réécrit depuis l'index, en LF quelle que soit la valeur de `core.autocrlf` (l'attribut `eol=lf` l'emporte).
# L'option `--index` met aussi à jour la taille et la date notées dans l'index : sans elle, `git status`
# signalerait ces fichiers comme modifiés alors que leur contenu est identique. Le contenu indexé n'est
# jamais modifié. Les listes de Git sont lues avec des séparateurs nuls (`-z`, `-0`) : aucun nom de fichier
# n'est interprété ni échappé, quels que soient ses caractères (espace, guillemet, tabulation, accent).
# Garantie : la recette ne supprime rien si `git diff` signale une modification non indexée, ni si l'un des
# fichiers à réécrire porte le bit `assume-unchanged` ou `skip-worktree`, que `git diff` ne voit pas : elle
# échoue alors en le disant. Un bit posé sur un fichier qui n'est pas à réécrire ne la gêne pas. Rien n'est
# garanti au-delà : par exemple, une modification faite pendant l'exécution même de la recette n'est pas
# détectée. Si la suppression d'un fichier échoue (fichier verrouillé sous Windows), les autres fichiers
# sont quand même réécrits, puis la recette échoue. Les fichiers non suivis ne sont pas touchés.

# Réécrit en LF les fichiers suivis restés en CRLF dans la copie de travail (Windows).
normaliser-fins-de-ligne:
    #!/usr/bin/env sh
    set -eu
    git diff --quiet || { echo "Modifications non indexées : indexe-les d'abord (git add)." >&2; exit 1; }
    dossier=$(mktemp -d)
    trap 'rm -rf "$dossier"' EXIT
    git ls-files -z --eol > "$dossier/etat"
    grep -z -E '^i/[a-z-]+ +w/(crlf|mixed) ' "$dossier/etat" > "$dossier/lignes" || [ $? -eq 1 ]
    cut -z -f2- "$dossier/lignes" > "$dossier/liste"
    [ -s "$dossier/liste" ] || exit 0
    # Un fichier marqué `assume-unchanged` (étiquette en minuscule) ou `skip-worktree` (`S`) échappe à `git diff`.
    xargs -0 git --literal-pathspecs ls-files -v -z -- < "$dossier/liste" > "$dossier/marques"
    trouve=0
    grep -z -q -E '^[a-zS] ' "$dossier/marques" || trouve=$?
    case "$trouve" in
        1) ;;
        0) echo "Fichier marqué assume-unchanged ou skip-worktree : rien n'a été supprimé." >&2; exit 1 ;;
        *) exit "$trouve" ;;
    esac
    echec=0
    xargs -0 rm -f -- < "$dossier/liste" || echec=$?
    git checkout-index --force --index -z --stdin < "$dossier/liste"
    exit "$echec"

# Les arguments arrivent en positionnels (`"$@"`) et ne sont jamais recopiés dans le texte du script : un
# argument contenant `;` ou `$(...)` reste un simple argument de pytest, il n'est pas exécuté comme une
# commande. Cette recette est autorisée sans confirmation dans `.claude/settings.json`, d'où la précaution.
# Recette à shebang (`sh`, présent avec Git pour Windows) : le shell PowerShell du reste du fichier n'offrirait
# pas la même protection. `[working-directory]` s'applique aussi aux recettes à shebang.

# Lance un test backend ciblé, sans seuil de couverture. Exemple : just test-back -k avancement
[positional-arguments]
[working-directory: 'backend']
test-back *args:
    #!/usr/bin/env sh
    set -eu
    exec uv run pytest --no-cov "$@"

# Même précaution que `test-back` : les arguments passent en positionnels, jamais recopiés dans le script.

# Lance un test frontend ciblé, sans couverture. Exemple : just test-front useEtatApi
[positional-arguments]
[working-directory: 'frontend']
test-front *args:
    #!/usr/bin/env sh
    set -eu
    exec pnpm exec vitest run "$@"

# Lance les tests de bout en bout (Playwright, Chromium) sur le site construit.
[working-directory: 'frontend']
e2e:
    pnpm e2e

# Régénère les types TypeScript de l'API à partir du schéma OpenAPI du backend. Sans argument, le client
# versionné (src/api/schema.d.ts) est réécrit ; `verifier-client` passe un autre chemin, relatif à `frontend/`.
# `--no-dev` : l'export du schéma n'a besoin que des dépendances d'exécution. Sans lui, `uv run` ajouterait
# le groupe `dev` à un environnement installé par `uv sync --no-dev` (job e2e de la CI). Avec lui, `uv run`
# n'ajoute rien et ne retire rien (il ne fait pas de synchronisation exacte) : en local, pytest, ruff et les
# autres outils restent installés.
# Recette à shebang (`sh`, présent avec Git pour Windows) : le chemin arrive en argument positionnel (`$1`),
# entre guillemets, et n'est jamais recopié dans le texte du script. Une valeur contenant `;`, `'` ou `$(...)`
# reste un simple nom de fichier, que ce soit sous Windows ou sous Linux. `quote()` ne conviendrait pas :
# il échappe pour `sh`, pas pour PowerShell, le shell des autres recettes sous Windows.
[positional-arguments]
client sortie="src/api/schema.d.ts":
    #!/usr/bin/env sh
    set -eu
    (cd backend && uv run --no-dev python -m tools.exporter_openapi ../frontend/openapi.json)
    cd frontend
    exec pnpm exec openapi-typescript openapi.json -o "$1"

# Le client généré est versionné (ADR 0013, issue #43) : un schéma d'API modifié sans `just client`
# laisserait le frontend typé sur une ancienne API. La recette régénère donc le client dans un dossier
# temporaire, hors des fichiers suivis, et le compare à la version commitée. La comparaison ignore le
# retour chariot de fin de ligne (CRLF sous Windows, LF sous Linux) : seul le contenu compte. Recette à
# shebang (`sh`, présent avec Git pour Windows), comme `normaliser-fins-de-ligne`.

# Vérifie que le client TypeScript généré (src/api/schema.d.ts) correspond au schéma OpenAPI de l'API.
verifier-client:
    #!/usr/bin/env sh
    set -eu
    dossier="frontend/{{dossier_client_verifie}}"
    mkdir -p "$dossier"
    trap 'rm -rf "$dossier"' EXIT
    "{{just_executable()}}" client "{{dossier_client_verifie}}/schema.d.ts"
    if ! diff --strip-trailing-cr -u frontend/src/api/schema.d.ts "$dossier/schema.d.ts"; then
        echo "Le client généré n'est pas à jour : lance 'just client' et commite frontend/src/api/schema.d.ts." >&2
        exit 1
    fi
    echo "Le client généré est à jour."

# Dossier (relatif à `frontend/`) où `verifier-client` régénère le client, hors des fichiers suivis.
dossier_client_verifie := "node_modules/.cache/client-verifie"

# Hooks pre-commit du frontend. Les fichiers arrivent depuis la racine du dépôt (`frontend/src/...`) :
# on retire le préfixe, car les outils tournent dans `frontend/`. Le retrait se fait dans le shell, argument
# par argument, et chaque argument reste entre guillemets : un nom de fichier contenant un espace, un `$(...)`
# ou un `;` est ainsi traité comme un simple nom, jamais comme du code à exécuter. Ce sont des recettes
# à shebang (`sh`, présent avec Git pour Windows) : le shell PowerShell du reste du fichier n'aurait pas la même
# protection.
# Limite connue sous Windows : just transmet mal aux hooks un nom de fichier qui contient une apostrophe.
# C'est un défaut de just, sans exécution de code : le hook échoue de façon visible, il ne laisse pas passer
# le fichier.
[positional-arguments]
[working-directory: 'frontend']
_hook-prettier *fichiers:
    #!/usr/bin/env sh
    set -eu
    for fichier in "$@"; do
        shift
        set -- "$@" "${fichier#frontend/}"
    done
    exec pnpm exec prettier --check --ignore-unknown "$@"

[positional-arguments]
[working-directory: 'frontend']
_hook-eslint *fichiers:
    #!/usr/bin/env sh
    set -eu
    for fichier in "$@"; do
        shift
        set -- "$@" "${fichier#frontend/}"
    done
    exec pnpm exec eslint --max-warnings 0 --no-warn-ignored "$@"
