"""Valeurs du domaine des chantiers que l'api expose telles quelles : les bornes de saisie.

L'api n'importe pas le domaine (contrat `api-sans-domain`) : elle lit ces bornes ici,
où elles sont republiées. Les schémas JSON et le domaine partagent ainsi une seule
source pour chaque limite, au lieu d'en recopier la valeur.
"""

from app.chantiers.domain.adresse import (
    LONGUEUR_CODE_POSTAL_MAX,
    LONGUEUR_VILLE_MAX,
    LONGUEUR_VOIE_MAX,
)
from app.chantiers.domain.chantier import LONGUEUR_CLIENT_MAX, LONGUEUR_NOM_MAX
from app.chantiers.domain.montant import CHIFFRES_MONTANT_MAX, DECIMALES_MONTANT

__all__ = [
    "CHIFFRES_MONTANT_MAX",
    "DECIMALES_MONTANT",
    "LONGUEUR_CLIENT_MAX",
    "LONGUEUR_CODE_POSTAL_MAX",
    "LONGUEUR_NOM_MAX",
    "LONGUEUR_VILLE_MAX",
    "LONGUEUR_VOIE_MAX",
]
