"""Résumé des étapes d'un chantier : compteurs et pourcentage d'avancement.

L'avancement est toujours calculé, jamais stocké : il ne peut donc pas diverger
de l'état réel des étapes (intent.md, §2.3).
"""

from collections.abc import Sequence
from dataclasses import dataclass

from app.etapes.domain.cycle import StatutEtape
from app.etapes.domain.etape import Etape
from app.shared.domain.erreurs import ValeurInvalideError

POURCENTAGE_MAX = 100


@dataclass(frozen=True, slots=True)
class ResumeEtapes:
    """Compteurs des étapes d'un chantier, d'où se déduit son avancement.

    `validees` compte les étapes validées par un chef, `a_valider` celles qui
    attendent sa décision. Une étape ne peut être dans les deux à la fois : leur
    somme ne dépasse donc jamais `total`.
    """

    total: int
    validees: int
    a_valider: int

    def __post_init__(self) -> None:
        """Refuse des compteurs qui ne peuvent pas décrire de vraies étapes.

        Lève :
            ValeurInvalideError : un compteur est négatif, ou les étapes validées et
                à valider sont plus nombreuses que le total.
        """
        if min(self.total, self.validees, self.a_valider) < 0:
            raise ValeurInvalideError("Un nombre d'étapes ne peut pas être négatif.")
        if self.validees + self.a_valider > self.total:
            raise ValeurInvalideError("Les étapes comptées dépassent le nombre total d'étapes.")

    @property
    def avancement(self) -> int:
        """Pourcentage d'étapes validées, de 0 à 100, arrondi à l'entier inférieur.

        Seules les étapes validées par un chef comptent : une étape signalée terminée
        n'est pas encore acquise. L'arrondi se fait vers le bas pour que 100 % signifie
        toujours « tout est validé » : 199 étapes validées sur 200 donnent 99 %, et non
        100 %. Sans étape, l'avancement vaut 0 %.
        """
        if not self.total:
            return 0
        return self.validees * POURCENTAGE_MAX // self.total


def resumer_etapes(etapes: Sequence[Etape]) -> ResumeEtapes:
    """Compte les étapes d'un chantier : toutes, les validées et celles à valider."""
    statuts = [etape.statut for etape in etapes]
    return ResumeEtapes(
        total=len(statuts),
        validees=statuts.count(StatutEtape.VALIDEE),
        a_valider=statuts.count(StatutEtape.TERMINEE_A_VALIDER),
    )
