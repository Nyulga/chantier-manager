"""Hook PreToolUse sur Bash : `git commit` et `git push` se font seulement sur la branche dev.

Règle du projet (CLAUDE.md) : on travaille uniquement sur `dev`, et on vérifie la branche avant
chaque commit. Ce hook le vérifie pour la session principale comme pour les sous-agents (la garde
des sous-agents leur refuse déjà tout commit, ADR 0017).

Il lit le texte de la commande : c'est un garde-fou contre les oublis, pas une barrière absolue.
Une commande qui change de branche puis commite (`git checkout main && git commit`) est refusée
aussi, car la branche est lue avant que la commande ne s'exécute. Une entrée sans commande Bash
est ignorée.
"""

import json
import os
import re
import sys
from pathlib import Path

BRANCHE = "dev"
CODE_BLOQUER = 2
# Un appel à git qui commite ou pousse, dans un même segment de la ligne de commande.
_GIT_QUI_ENREGISTRE = re.compile(r"\bgit\b[^;&|\n]*\b(commit|push)\b")
# Un appel à git qui change de branche.
_GIT_QUI_CHANGE_DE_BRANCHE = re.compile(r"\bgit\b[^;&|\n]*\b(checkout|switch)\b")
# Contenu de `.git/HEAD` quand une branche est active ; sinon (HEAD détachée), c'est un commit.
_PREFIXE_BRANCHE = "ref: refs/heads/"


def _commande(brut: bytes) -> str:
    """Renvoie la commande Bash de l'appel, ou une chaîne vide si l'entrée n'en contient pas."""
    try:
        commande = json.loads(brut.decode("utf-8"))["tool_input"]["command"]
    except (ValueError, KeyError, TypeError):
        return ""
    return commande if isinstance(commande, str) else ""


def _branche_courante(projet: Path) -> str:
    """Lit la branche active dans `.git/HEAD`, sans lancer git ; vide si elle est inconnue."""
    try:
        tete = (projet / ".git" / "HEAD").read_text(encoding="utf-8").strip()
    except OSError:
        return ""
    return tete.removeprefix(_PREFIXE_BRANCHE) if tete.startswith(_PREFIXE_BRANCHE) else ""


def main() -> int:
    """Lit l'appel sur l'entrée standard ; renvoie 2 pour le bloquer, 0 pour le laisser faire."""
    commande = _commande(sys.stdin.buffer.read())
    if not _GIT_QUI_ENREGISTRE.search(commande):
        return 0
    branche = _branche_courante(Path(os.environ.get("CLAUDE_PROJECT_DIR") or "."))
    if branche == BRANCHE and not _GIT_QUI_CHANGE_DE_BRANCHE.search(commande):
        return 0
    message = (
        "Hook du projet : git commit et git push se font seulement sur la branche dev "
        f"(branche actuelle : « {branche or 'inconnue'} »), et jamais dans la même commande "
        "qu'un changement de branche. Repasse sur dev, ou demande à l'utilisateur.\n"
    )
    sys.stderr.buffer.write(message.encode("utf-8"))
    return CODE_BLOQUER


if __name__ == "__main__":
    sys.exit(main())
