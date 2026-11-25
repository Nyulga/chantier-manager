#!/bin/bash
# Hook PostToolUse sur Edit|Write : lance ESLint sur le fichier du frontend que l'agent vient de
# modifier. Un échec renvoie les erreurs à l'agent (code 2), qui doit les corriger.
#
# Adapté au projet :
# - le chemin est lu par Python (`jq` n'est pas installé sur le poste) ;
# - seuls les fichiers de `frontend/` sont contrôlés, car la configuration d'ESLint est là ;
# - ESLint est celui du projet (`pnpm exec`), jamais téléchargé (`npx` pourrait le faire).
fichier=$(python -I -c 'import json, sys; print(json.load(sys.stdin).get("tool_input", {}).get("file_path", ""))') || exit 0
case "$fichier" in
  *.ts|*.tsx|*.js|*.jsx) ;;
  *) exit 0 ;;
esac
case "${fichier//\\//}" in
  */frontend/*) ;;
  *) exit 0 ;;
esac
cd "${CLAUDE_PROJECT_DIR:-.}/frontend" || exit 1
if ! sortie=$(pnpm exec eslint "$fichier" 2>&1); then
  echo "Lint en échec sur $fichier :" >&2
  echo "$sortie" >&2
  exit 2
fi
exit 0
