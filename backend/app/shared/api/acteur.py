"""Dépendance `acteur_courant` : l'acteur d'une requête, tiré du profil choisi dans l'interface."""

from typing import Annotated

from fastapi import Depends, Header

from app.shared.api.erreurs import ProfilInvalideError
from app.shared.domain.acteur import Acteur, Role

EN_TETE_PROFIL = "X-Profil"


def acteur_courant(
    x_profil: Annotated[
        str | None,
        Header(description="Profil choisi dans l'interface : `chef` ou `ouvrier`."),
    ] = None,
) -> Acteur:
    """Construit l'acteur à partir de l'en-tête `X-Profil`.

    Le squelette n'a pas d'authentification (docs/plan/squelette.md) : le profil
    est une simple déclaration, protégée seulement par le mot de passe du site. En
    phase 2, cette fonction lira le jeton de session au lieu de l'en-tête, sans
    changer ni les routes ni les cas d'usage.

    Lève :
        ProfilInvalideError : l'en-tête est absent ou ne vaut ni `chef` ni `ouvrier`.
    """
    try:
        # Un en-tête absent est traité comme un profil vide, donc inconnu.
        return Acteur(Role(x_profil or ""))
    except ValueError:
        raise ProfilInvalideError from None


# Les routes déclarent `acteur: ActeurCourant` : elles n'importent ainsi ni le
# domaine ni FastAPI pour obtenir l'acteur (contrat `api-sans-domain`).
ActeurCourant = Annotated[Acteur, Depends(acteur_courant)]
