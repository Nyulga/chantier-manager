"""Valeurs du domaine des étapes que l'api expose telles quelles : bornes de saisie et rôles.

L'api n'importe pas le domaine (contrat `api-sans-domain`) : elle lit ces valeurs ici,
où elles sont republiées. Les schémas JSON et le domaine partagent ainsi une seule
source, au lieu d'en recopier les valeurs.
"""

from app.etapes.domain.etape import (
    LONGUEUR_COMMENTAIRE_MAX,
    LONGUEUR_TITRE_MAX,
    VERSION_INITIALE,
)
from app.shared.domain.acteur import Role

__all__ = ["LONGUEUR_COMMENTAIRE_MAX", "LONGUEUR_TITRE_MAX", "VERSION_INITIALE", "Role"]
