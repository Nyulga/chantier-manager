#!/bin/bash
# Hook PostToolUse sur Edit|Write : lance ruff sur le fichier Python du backend que l'agent vient
# de modifier. Un échec renvoie les erreurs à l'agent (code 2), qui doit les corriger tout de
# suite, au lieu d'attendre `just verifier`. Pendant Python de `lint-apres-modif.sh` (ESLint).
#
# - le chemin est lu par Python, en octets (UTF-8), comme dans le hook ESLint ;
# - seuls les fichiers `.py` du dossier `backend/` du projet sont contrôlés ;
# - ruff est celui de l'environnement du backend (Windows, puis Linux), sinon celui du PATH ; s'il
#   est introuvable, ou si Python manque, le contrôle est sauté (`exit 0`) : la CI le refait ;
# - `--force-exclude` : un fichier exclu par la configuration (migrations générées) reste ignoré.
fichier=$(python -I -c 'import json, sys; print(json.load(sys.stdin.buffer).get("tool_input", {}).get("file_path", ""))') || exit 0
case "$fichier" in
  *.py) ;;
  *) exit 0 ;;
esac
# Les chemins Windows arrivent avec des `\` : on les compare avec des `/`, casse ignorée, et la
# forme Git Bash `/c/…` est ramenée à `c:/…`.
comparable() { printf '%s' "$1" | tr '\\' '/' | tr '[:upper:]' '[:lower:]' | sed -E 's#^/([a-z])/#\1:/#'; }
projet=$(comparable "${CLAUDE_PROJECT_DIR:-.}")
compare=$(comparable "$fichier")
case "$compare" in
  "$projet"/backend/*) ;;
  *) exit 0 ;;
esac
cd "${CLAUDE_PROJECT_DIR:-.}/backend" || exit 1
ruff=.venv/Scripts/ruff.exe
[ -x "$ruff" ] || ruff=.venv/bin/ruff
[ -x "$ruff" ] || ruff=$(command -v ruff) || exit 0
if ! sortie=$("$ruff" check --quiet --force-exclude -- "$fichier" 2>&1 && "$ruff" format --check --force-exclude -- "$fichier" 2>&1); then
  echo "Ruff en échec sur $fichier :" >&2
  echo "$sortie" >&2
  exit 2
fi
exit 0
