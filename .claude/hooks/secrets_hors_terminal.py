"""Hook PreToolUse sur Bash : aucune commande ne lit un fichier de secrets.

Les règles `deny` de `.claude/settings.json` interdisent de lire `.env`, `.env.local`,
`~/.claude.json` et `~/.ssh` avec l'outil Read, mais pas par le terminal (`cat .env`). Ce hook
refuse toute commande Bash qui nomme l'un de ces fichiers, pour la session principale comme pour
les sous-agents. `.env.example`, qui ne contient pas de secret, reste permis.

Il lit le texte de la commande : c'est un garde-fou contre les oublis, pas une barrière absolue
(un nom construit par la commande elle-même n'est pas vu).
"""

import json
import re
import sys

CODE_BLOQUER = 2
# Noms de fichiers de secrets, reconnus seulement comme nom entier : `migrations/env.py`,
# `.envrc` et `.env.example` ne sont pas concernés.
_FICHIERS_DE_SECRETS = re.compile(
    r"(?<![\w.-])\.env(?:\.(?!example(?![\w.-]))[\w-]+)?(?![\w.-])"
    r"|\.claude\.json"
    r"|(?<![\w.-])\.ssh(?![\w.-])"
)


def _commande(brut: bytes) -> str:
    """Renvoie la commande Bash de l'appel, ou une chaîne vide si l'entrée n'en contient pas."""
    try:
        commande = json.loads(brut.decode("utf-8"))["tool_input"]["command"]
    except (ValueError, KeyError, TypeError):
        return ""
    return commande if isinstance(commande, str) else ""


def main() -> int:
    """Lit l'appel sur l'entrée standard ; renvoie 2 pour le bloquer, 0 pour le laisser faire."""
    if not _FICHIERS_DE_SECRETS.search(_commande(sys.stdin.buffer.read())):
        return 0
    message = (
        "Hook du projet : cette commande nomme un fichier de secrets (.env, ~/.claude.json, "
        "~/.ssh), que Claude ne doit jamais lire. Demande à l'utilisateur de le faire lui-même.\n"
    )
    sys.stderr.buffer.write(message.encode("utf-8"))
    return CODE_BLOQUER


if __name__ == "__main__":
    sys.exit(main())
