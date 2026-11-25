"""Comparaison des chemins de fichier pour la garde des sous-agents.

Les chemins sont comparés comme du texte, de la même façon sous Windows (poste) et sous Linux (CI) :
`/` partout, `.` et `..` résolus, casse ignorée. Le disque n'est jamais consulté : les formes que
Windows ramènerait à un autre fichier sont donc refusées à part (`est_suspect`).
"""

import posixpath
import re
from pathlib import Path

_CHEMIN_ABSOLU = re.compile(r"[a-z]:/|/")
_LECTEUR = re.compile(r"[a-z]:/")
# Git Bash écrit `C:\Users` sous la forme `/c/Users`.
_LECTEUR_GIT_BASH = re.compile(r"/([a-z])/")
_PREFIXE_LECTEUR = re.compile(r"[A-Za-z]:")


def normaliser(chemin: str) -> str:
    """Rend un chemin comparable : `/` partout, `.` et `..` résolus, casse ignorée."""
    return posixpath.normpath(chemin.replace("\\", "/")).casefold()


def est_suspect(chemin: str) -> bool:
    """Dit si le chemin a une forme que Windows ramène à un autre nom que celui qu'on compare.

    Windows retire le point ou l'espace final d'un nom (`x.py.` désigne `x.py`), lit `x.py::$DATA`
    comme `x.py`, et les chemins réseau (`//serveur/x`, `\\\\?\\C:\\x`) contournent la comparaison
    avec la racine. La garde refuse ces formes plutôt que de se tromper de fichier.
    """
    texte = chemin.replace("\\", "/")
    if texte.startswith("//"):
        return True
    sans_lecteur = texte[2:] if _PREFIXE_LECTEUR.match(texte) else texte
    if ":" in sans_lecteur:
        return True
    composants = (c for c in texte.split("/") if c not in {"", ".", ".."})
    return any(c != c.rstrip(". ") for c in composants)


def chemin_relatif(chemin: str, racine: str | Path) -> str | None:
    """Donne le chemin relatif à la racine du dépôt, ou `None` s'il est hors du dépôt.

    Un chemin non absolu est rattaché à la racine. Quand la racine est un chemin Windows, la forme
    de Git Bash (`/c/Users/...`) est ramenée à la forme Windows (`c:/users/...`) ; sous Linux, un
    dossier `/c/` reste un dossier ordinaire.
    """
    base = normaliser(str(racine)).rstrip("/")
    complet = normaliser(chemin)
    if _LECTEUR.match(base) and _LECTEUR_GIT_BASH.match(complet):
        complet = f"{complet[1]}:/{complet[3:]}"
    if not _CHEMIN_ABSOLU.match(complet):
        complet = normaliser(f"{base}/{chemin}")
    if complet == base:
        return "."
    prefixe = f"{base}/"
    return complet.removeprefix(prefixe) if complet.startswith(prefixe) else None
