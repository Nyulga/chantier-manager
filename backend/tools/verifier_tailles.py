"""Vérifie les limites de taille et de forme du code Python : fichiers et fonctions.

Un fichier ne dépasse pas 300 lignes, une fonction ne dépasse pas 40 lignes et
ses blocs (`if`, `for`, `while`, `with`, `try`, `match`) ne s'imbriquent pas sur
plus de 3 niveaux (règle 00, §4). Ruff mesure la complexité et le nombre
d'instructions, mais ni les lignes ni la profondeur : ce script complète ce
contrôle (ADR 0005). Il ne dépend que de la bibliothèque standard, pour pouvoir
tourner partout, y compris dans la CI.

Usage : python tools/verifier_tailles.py [chemin ...]
Sans argument, il examine `app`, `tools` et `tests`. Le code de sortie vaut 0
si tout est conforme, 1 si une limite est dépassée et 2 si un chemin n'existe pas.
"""

import ast
import sys
from collections.abc import Iterator, Sequence
from dataclasses import dataclass
from pathlib import Path

MAX_LIGNES_FICHIER = 300
MAX_LIGNES_FONCTION = 40
MAX_PROFONDEUR = 3
RACINES_PAR_DEFAUT = ("app", "tools", "tests")
DOSSIERS_IGNORES = frozenset({".venv", "__pycache__", ".mypy_cache", ".ruff_cache"})
CODE_VIOLATION = 1
CODE_CHEMIN_INTROUVABLE = 2


@dataclass(frozen=True)
class Violation:
    """Une limite de taille dépassée, avec l'endroit exact où la corriger."""

    chemin: Path
    ligne: int
    message: str

    def __str__(self) -> str:
        """Met la violation en forme `chemin:ligne: message`, comme les outils de lint."""
        return f"{self.chemin}:{self.ligne}: {self.message}"


def lister_fichiers_python(racines: Sequence[Path]) -> Iterator[Path]:
    """Énumère les fichiers `.py` des racines données, qui sont des dossiers ou des fichiers.

    Les dossiers générés (environnement virtuel, caches) sont ignorés : leur taille
    n'est pas de notre responsabilité.
    """
    for racine in racines:
        candidats = [racine] if racine.is_file() else sorted(racine.rglob("*.py"))
        for chemin in candidats:
            if not DOSSIERS_IGNORES.intersection(chemin.parts):
                yield chemin


def verifier_fichier(chemin: Path) -> list[Violation]:
    """Mesure un fichier : sa longueur, puis celle de chacune de ses fonctions."""
    source = chemin.read_text(encoding="utf-8")
    nombre_de_lignes = len(source.splitlines())
    violations: list[Violation] = []
    if nombre_de_lignes > MAX_LIGNES_FICHIER:
        message = f"fichier de {nombre_de_lignes} lignes (maximum {MAX_LIGNES_FICHIER})"
        violations.append(Violation(chemin, 1, message))
    try:
        arbre = ast.parse(source, filename=str(chemin))
    except SyntaxError as erreur:
        # Un fichier illisible ne doit jamais passer pour conforme.
        message = f"syntaxe invalide, mesure impossible : {erreur.msg}"
        return [*violations, Violation(chemin, erreur.lineno or 1, message)]
    return [
        *violations,
        *_fonctions_trop_longues(arbre, chemin),
        *_fonctions_trop_imbriquees(arbre, chemin),
    ]


def _fonctions_trop_longues(arbre: ast.AST, chemin: Path) -> list[Violation]:
    """Repère les fonctions et méthodes, imbriquées comprises, qui dépassent la limite."""
    violations: list[Violation] = []
    for noeud in ast.walk(arbre):
        if not isinstance(noeud, ast.FunctionDef | ast.AsyncFunctionDef):
            continue
        # Les lignes comptent de `def` à la dernière instruction, docstring comprise.
        nombre_de_lignes = (noeud.end_lineno or noeud.lineno) - noeud.lineno + 1
        if nombre_de_lignes > MAX_LIGNES_FONCTION:
            message = (
                f"fonction « {noeud.name} » de {nombre_de_lignes} lignes "
                f"(maximum {MAX_LIGNES_FONCTION})"
            )
            violations.append(Violation(chemin, noeud.lineno, message))
    return sorted(violations, key=lambda violation: violation.ligne)


def _est_un_bloc(instruction: ast.stmt) -> bool:
    """Dit si l'instruction ouvre un bloc qui compte dans la profondeur d'imbrication."""
    return isinstance(
        instruction,
        ast.If
        | ast.For
        | ast.AsyncFor
        | ast.While
        | ast.With
        | ast.AsyncWith
        | ast.Try
        | ast.TryStar
        | ast.Match,
    )


def _sous_blocs(instruction: ast.stmt) -> list[list[ast.stmt]]:
    """Liste les suites d'instructions contenues dans un bloc (corps, `else`, `except`, `case`)."""
    suites: list[list[ast.stmt]] = []
    for nom in ("body", "orelse", "finalbody"):
        suites.append(getattr(instruction, nom, []))
    suites.extend(gestionnaire.body for gestionnaire in getattr(instruction, "handlers", []))
    suites.extend(cas.body for cas in getattr(instruction, "cases", []))
    return suites


def _est_un_elif(instruction: ast.stmt, parent: ast.stmt) -> bool:
    """Reconnaît un `elif` : un `if` seul dans le `else`, écrit à la colonne de son parent.

    L'arbre syntaxique range un `elif` dans le `else` du `if` précédent. Il ne doit
    pas compter comme un niveau de plus, sinon une simple chaîne de `elif` serait
    sanctionnée alors qu'elle se lit à plat. Un vrai `else:` suivi d'un `if` est
    forcément indenté plus à droite : il garde son niveau.
    """
    return (
        isinstance(parent, ast.If)
        and isinstance(instruction, ast.If)
        and instruction.col_offset == parent.col_offset
        and parent.orelse == [instruction]
    )


def _bloc_trop_profond(
    suite: list[ast.stmt], profondeur: int, parent: ast.stmt | None = None
) -> ast.stmt | None:
    """Renvoie le premier bloc de la suite qui dépasse la profondeur maximale, s'il y en a un.

    Les fonctions et classes internes sont ignorées : elles sont mesurées à part,
    avec leur propre profondeur de départ.
    """
    for instruction in suite:
        if not _est_un_bloc(instruction):
            continue
        niveau = profondeur if parent and _est_un_elif(instruction, parent) else profondeur + 1
        if niveau > MAX_PROFONDEUR:
            return instruction
        for sous_suite in _sous_blocs(instruction):
            fautif = _bloc_trop_profond(sous_suite, niveau, instruction)
            if fautif is not None:
                return fautif
    return None


def _fonctions_trop_imbriquees(arbre: ast.AST, chemin: Path) -> list[Violation]:
    """Repère les fonctions et méthodes dont les blocs s'imbriquent au-delà de la limite."""
    violations: list[Violation] = []
    for noeud in ast.walk(arbre):
        if not isinstance(noeud, ast.FunctionDef | ast.AsyncFunctionDef):
            continue
        fautif = _bloc_trop_profond(noeud.body, 0)
        if fautif is not None:
            message = (
                f"fonction « {noeud.name} » : blocs imbriqués sur plus de "
                f"{MAX_PROFONDEUR} niveaux ; utiliser un retour anticipé ou extraire une fonction"
            )
            violations.append(Violation(chemin, fautif.lineno, message))
    return sorted(violations, key=lambda violation: violation.ligne)


def verifier(racines: Sequence[Path]) -> list[Violation]:
    """Mesure tous les fichiers Python des racines données."""
    return [
        violation
        for chemin in lister_fichiers_python(racines)
        for violation in verifier_fichier(chemin)
    ]


def main(arguments: Sequence[str]) -> int:
    """Point d'entrée en ligne de commande ; renvoie le code de sortie du processus."""
    racines = [Path(argument) for argument in (arguments or RACINES_PAR_DEFAUT)]
    # Un chemin absent donnerait un faux « tout est conforme » : on refuse plutôt.
    introuvables = [racine for racine in racines if not racine.exists()]
    if introuvables:
        noms = ", ".join(str(racine) for racine in introuvables)
        print(f"Chemin introuvable : {noms}", file=sys.stderr)
        return CODE_CHEMIN_INTROUVABLE
    violations = verifier(racines)
    for violation in violations:
        print(violation)
    if violations:
        return CODE_VIOLATION
    print(
        "Limites de taille respectées : tous les fichiers et toutes les fonctions sont conformes."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
