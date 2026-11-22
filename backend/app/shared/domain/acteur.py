"""L'acteur d'un cas d'usage : la personne qui agit, réduite à ce dont le métier a besoin."""

from dataclasses import dataclass
from enum import StrEnum


class Role(StrEnum):
    """Rôle d'un utilisateur, qui détermine ce qu'il a le droit de faire."""

    CHEF = "chef"
    OUVRIER = "ouvrier"


@dataclass(frozen=True, slots=True)
class Acteur:
    """La personne qui exécute un cas d'usage, passée en paramètre à chaque service.

    Dans le squelette, il n'y a pas de compte : l'acteur ne porte que le rôle choisi
    dans le sélecteur de profil (docs/plan/squelette.md). L'identifiant de
    l'utilisateur s'ajoutera avec l'authentification, sans toucher aux règles.
    """

    role: Role
