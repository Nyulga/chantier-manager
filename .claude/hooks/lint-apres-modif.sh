#!/bin/bash
# Hook PostToolUse sur Edit|Write : lance ESLint sur le fichier du frontend que l'agent vient de
# modifier. Un échec renvoie les erreurs à l'agent (code 2), qui doit les corriger tout de suite.
#
# Ce script part de l'exemple de la formation (`jq` puis `npx eslint`), adapté au projet :
# - le chemin est lu par Python, car `jq` n'est pas installé sur le poste. L'entrée est lue en
#   octets (UTF-8), sinon Windows la décoderait en cp1252 et un caractère comme « ” » ferait
#   sauter le lint ;
# - si Python manque ou que l'entrée est illisible, le lint est sauté (`exit 0`) : c'est un
#   confort, la CI relance ESLint de toute façon ;
# - seuls les fichiers du dossier `frontend/` du projet sont contrôlés, car la configuration
#   d'ESLint est là ;
# - ESLint est celui du projet (`pnpm exec`), jamais téléchargé comme `npx` pourrait le faire, et
#   aussi strict que la CI (`--max-warnings 0`).
fichier=$(python -I -c 'import json, sys; print(json.load(sys.stdin.buffer).get("tool_input", {}).get("file_path", ""))') || exit 0
case "$fichier" in
  *.ts|*.tsx|*.js|*.jsx) ;;
  *) exit 0 ;;
esac
# Les chemins Windows arrivent avec des `\` : on les compare avec des `/`, casse ignorée.
projet=$(printf '%s' "${CLAUDE_PROJECT_DIR:-.}" | tr '\\' '/' | tr '[:upper:]' '[:lower:]')
compare=$(printf '%s' "$fichier" | tr '\\' '/' | tr '[:upper:]' '[:lower:]')
case "$compare" in
  "$projet"/frontend/*) ;;
  *) exit 0 ;;
esac
cd "${CLAUDE_PROJECT_DIR:-.}/frontend" || exit 1
if ! sortie=$(pnpm exec eslint --max-warnings 0 -- "$fichier" 2>&1); then
  echo "Lint en échec sur $fichier :" >&2
  echo "$sortie" >&2
  exit 2
fi
exit 0
