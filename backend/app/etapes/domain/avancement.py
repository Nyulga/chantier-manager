"""Calcul de l'avancement d'un chantier à partir de ses étapes.

L'avancement est toujours calculé, jamais stocké : il ne peut donc pas diverger
de l'état réel des étapes (intent.md, §2.3).
"""

from collections.abc import Sequence

from app.etapes.domain.cycle import StatutEtape
from app.etapes.domain.etape import Etape

POURCENTAGE_MAX = 100


def calculer_avancement(etapes: Sequence[Etape]) -> int:
    """Renvoie le pourcentage d'étapes validées, de 0 à 100, arrondi à l'entier inférieur.

    Seules les étapes validées par un chef comptent : une étape signalée terminée
    n'est pas encore acquise. L'arrondi se fait vers le bas pour que 100 % signifie
    toujours « tout est validé » : 199 étapes validées sur 200 donnent 99 %, et non
    100 %. Sans étape, l'avancement vaut 0 %.
    """
    if not etapes:
        return 0
    validees = sum(1 for etape in etapes if etape.statut is StatutEtape.VALIDEE)
    return validees * POURCENTAGE_MAX // len(etapes)
