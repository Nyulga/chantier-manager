"""Point d'entrée du hook `PreToolUse` qui garde les sous-agents (ADR 0017).

Le hook de `.claude/settings.json` lance ce script par `python -I`, sans uv, pour ne pas ralentir
chaque action ; la logique est dans le paquet `tools.garde`. Ce point d'entrée applique deux
principes :
- la session principale (le coordinateur, sans `agent_type`) passe avant toute autre vérification :
  une garde en panne ne doit pas l'empêcher de travailler, ni de réparer la garde ;
- pour un sous-agent, toute panne bloque l'appel (code de sortie 2, le seul que Claude Code lit
  comme un blocage) : Python trop ancien, garde impossible à charger, erreur inattendue. Le hook
  ajoute `|| exit 2` pour le cas où Python lui-même est introuvable.

Python 3.13 au moins est requis (`PurePosixPath.full_match`).
"""

import json
import os
import sys
from pathlib import Path

# Même valeur que `tools.garde.protocole.CODE_BLOQUER`, qu'on ne peut pas importer avant d'avoir
# vérifié la version de Python.
CODE_BLOQUER = 2
VERSION_MINIMALE = (3, 13)
_DOSSIER_BACKEND = Path(__file__).resolve().parents[1]


def est_session_principale(brut: bytes) -> bool:
    """Dit si l'appel vient de la session principale : un objet JSON sans `agent_type`.

    Une entrée illisible n'est pas la session principale : elle sera bloquée plus loin.
    """
    try:
        entree = json.loads(brut.decode("utf-8"))
    except ValueError:
        return False
    return isinstance(entree, dict) and not entree.get("agent_type")


def _ecrire_erreur(message: str) -> None:
    # En UTF-8 quel que soit l'encodage de la console : sous Windows, `python -I` écrirait sinon
    # en cp1252, et Claude Code afficherait des accents cassés.
    sys.stderr.flush()
    sys.stderr.buffer.write(message.encode("utf-8"))
    sys.stderr.buffer.flush()


def _juger(brut: bytes, racine: str | Path) -> int:
    """Fait juger l'appel par le paquet de la garde, écrit la réponse et renvoie le code."""
    # `python -I` n'ajoute pas le dossier du script au chemin des modules. On ajoute le dossier
    # du backend en dernier, pour qu'aucun fichier qui s'y trouve ne masque un module standard.
    if str(_DOSSIER_BACKEND) not in sys.path:
        sys.path.append(str(_DOSSIER_BACKEND))
    from tools.garde.protocole import traiter

    reponse = traiter(brut, racine)
    sys.stdout.write(reponse.sortie)
    _ecrire_erreur(reponse.erreur)
    return reponse.code


def main() -> int:
    """Lit l'appel sur l'entrée standard et écrit la réponse ; renvoie le code de sortie."""
    brut = sys.stdin.buffer.read()
    if est_session_principale(brut):
        return 0
    if sys.version_info < VERSION_MINIMALE:
        _ecrire_erreur("Garde des agents : Python 3.13 au moins est requis ; appel bloqué.\n")
        return CODE_BLOQUER
    racine = os.environ.get("CLAUDE_PROJECT_DIR") or _DOSSIER_BACKEND.parent
    try:
        return _juger(brut, racine)
    except Exception as erreur:
        # Même principe que dans `traiter` : une garde qui ne sait pas juger bloque.
        _ecrire_erreur(f"Garde des agents : erreur interne ({type(erreur).__name__}).\n")
        return CODE_BLOQUER


if __name__ == "__main__":
    sys.exit(main())
