"""Vérifie qu'aucun contrôle de qualité n'est désactivé dans le code Python.

La règle 00 (§4) interdit de contourner un contrôle : `# noqa`, `# type: ignore`,
`# pragma: no cover` ou `no branch`, `# nosec`, `# mypy: ignore-errors` et `typing.cast`.
Ruff, mypy, coverage et bandit laissent tous passer ces contournements ; ce script
les refuse (ADR 0005). Un contournement inévitable demande l'accord écrit du
propriétaire, puis une évolution explicite de cette règle de contrôle.

Les commentaires sont lus avec `tokenize` et les `cast` avec `ast` : une chaîne de
caractères qui contient « noqa » n'est donc jamais prise pour un commentaire.

Usage : python -m tools.verifier_desactivations [chemin ...]
Sans argument, il examine `app`, `tools`, `migrations` et `tests`. Le code de sortie
vaut 0 si tout est conforme, 1 si une désactivation est trouvée et 2 si un chemin
n'existe pas.
"""

import ast
import io
import re
import sys
import tokenize
from collections.abc import Iterator, Sequence
from pathlib import Path

from tools.verifier_tailles import Violation, lister_fichiers_python

RACINES_PAR_DEFAUT = ("app", "tools", "migrations", "tests")
CODE_VIOLATION = 1
CODE_CHEMIN_INTROUVABLE = 2
MODULES_DU_TYPAGE = frozenset({"typing", "typing_extensions"})
# Chaque motif décrit un commentaire de désactivation ; la casse et les espaces sont tolérés.
MOTIFS_DE_COMMENTAIRE = {
    "noqa": re.compile(r"\bnoqa\b", re.IGNORECASE),
    "type: ignore": re.compile(r"\btype:\s*ignore\b", re.IGNORECASE),
    "pragma: no cover / no branch": re.compile(r"\bpragma:\s*no\s*(cover|branch)\b", re.IGNORECASE),
    "nosec": re.compile(r"\bnosec\b", re.IGNORECASE),
    "mypy: ignore-errors": re.compile(r"\bmypy:\s*ignore-errors\b", re.IGNORECASE),
}


def _commentaires_interdits(source: str, chemin: Path) -> Iterator[Violation]:
    """Repère les commentaires qui désactivent un contrôle, sans regarder les chaînes."""
    for jeton in tokenize.generate_tokens(io.StringIO(source).readline):
        if jeton.type != tokenize.COMMENT:
            continue
        for nom, motif in MOTIFS_DE_COMMENTAIRE.items():
            if motif.search(jeton.string):
                yield Violation(chemin, jeton.start[0], f"désactivation interdite : « {nom} »")


def _alias_du_module_typage(arbre: ast.AST) -> frozenset[str]:
    """Liste les noms sous lesquels `typing` est importé (`import typing as t` donne `t`)."""
    alias = set(MODULES_DU_TYPAGE)
    for noeud in ast.walk(arbre):
        if isinstance(noeud, ast.Import):
            alias.update((a.asname or a.name) for a in noeud.names if a.name in MODULES_DU_TYPAGE)
    return frozenset(alias)


def _est_un_import_de_cast(noeud: ast.AST) -> bool:
    """Dit si le noeud est `from typing import cast`, avec ou sans alias."""
    return (
        isinstance(noeud, ast.ImportFrom)
        and noeud.module in MODULES_DU_TYPAGE
        and any(nom.name == "cast" for nom in noeud.names)
    )


def _est_un_appel_de_cast(noeud: ast.AST, alias: frozenset[str]) -> bool:
    """Dit si le noeud est `typing.cast`, le module pouvant porter un alias."""
    return (
        isinstance(noeud, ast.Attribute)
        and noeud.attr == "cast"
        and isinstance(noeud.value, ast.Name)
        and noeud.value.id in alias
    )


def _usages_de_cast(arbre: ast.AST, chemin: Path) -> Iterator[Violation]:
    """Repère l'import de `cast` et son appel par le module (`typing.cast(...)`)."""
    alias = _alias_du_module_typage(arbre)
    message = "désactivation interdite : « cast » (le typage doit être juste, pas forcé)"
    for noeud in ast.walk(arbre):
        if _est_un_import_de_cast(noeud) or _est_un_appel_de_cast(noeud, alias):
            # Les deux formes reconnues portent toujours un numéro de ligne.
            yield Violation(chemin, getattr(noeud, "lineno", 1), message)


def verifier_fichier(chemin: Path) -> list[Violation]:
    """Cherche les désactivations d'un fichier, triées par ligne."""
    source = chemin.read_text(encoding="utf-8")
    try:
        arbre = ast.parse(source, filename=str(chemin))
        violations = [*_commentaires_interdits(source, chemin), *_usages_de_cast(arbre, chemin)]
    except (SyntaxError, tokenize.TokenError) as erreur:
        # Un fichier illisible ne doit jamais passer pour conforme.
        message = f"syntaxe invalide, contrôle impossible : {erreur}"
        return [Violation(chemin, getattr(erreur, "lineno", None) or 1, message)]
    return sorted(violations, key=lambda violation: violation.ligne)


def main(arguments: Sequence[str]) -> int:
    """Point d'entrée en ligne de commande ; renvoie le code de sortie du processus."""
    racines = [Path(argument) for argument in (arguments or RACINES_PAR_DEFAUT)]
    # Un chemin absent donnerait un faux « tout est conforme » : on refuse plutôt.
    introuvables = [racine for racine in racines if not racine.exists()]
    if introuvables:
        noms = ", ".join(str(racine) for racine in introuvables)
        print(f"Chemin introuvable : {noms}", file=sys.stderr)
        return CODE_CHEMIN_INTROUVABLE
    violations = [
        violation
        for chemin in lister_fichiers_python(racines)
        for violation in verifier_fichier(chemin)
    ]
    for violation in violations:
        print(violation)
    if violations:
        return CODE_VIOLATION
    print("Aucune désactivation de contrôle : le code respecte la règle 00 (§4).")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
