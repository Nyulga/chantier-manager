"""Exporte le schéma OpenAPI de l'application dans un fichier JSON.

Le frontend génère ses types TypeScript à partir de ce fichier (recette `client`
du justfile) : le contrat d'API est ainsi écrit une seule fois, dans le backend.
Le schéma est construit sans démarrer de serveur ni toucher à la base.

Usage : python -m tools.exporter_openapi <fichier de sortie>
Il faut le lancer depuis le dossier `backend`, pour que le paquet `app` soit importable.
"""

import json
import sys
from collections.abc import Sequence
from pathlib import Path

from app.main import creer_application

CODE_USAGE = 2


def schema_openapi() -> str:
    """Renvoie le schéma OpenAPI en JSON.

    Les clés sont triées et la mise en forme est fixe : deux exports successifs
    sont identiques octet pour octet, ce qui évite du bruit dans les différences.
    """
    schema = creer_application().openapi()
    return json.dumps(schema, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def main(arguments: Sequence[str]) -> int:
    """Point d'entrée en ligne de commande ; renvoie le code de sortie du processus."""
    if len(arguments) != 1:
        print("Usage : python -m tools.exporter_openapi <fichier de sortie>", file=sys.stderr)
        return CODE_USAGE
    # L'encodage est imposé : sous Windows, il dépendrait sinon de la page de code.
    Path(arguments[0]).write_text(schema_openapi(), encoding="utf-8", newline="\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
