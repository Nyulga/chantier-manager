"""Objet valeur `Delai` : le temps qui reste avant l'échéance d'un chantier, ou le retard pris."""

from dataclasses import dataclass
from datetime import date

from app.shared.domain.erreurs import ValeurInvalideError

# Un chantier en retard a dépassé son échéance d'au moins un jour entier.
RETARD_MINIMAL = 1


@dataclass(frozen=True, slots=True)
class Delai:
    """Écart entre la date du jour et l'échéance d'un chantier, compté en jours entiers.

    `jours_restants` est toujours positif ou nul, pour que l'interface n'ait jamais
    à interpréter un signe. Son sens dépend de `en_retard` :
    - `en_retard` faux : c'est le nombre de jours avant l'échéance (0 le jour même) ;
    - `en_retard` vrai : c'est le nombre de jours écoulés depuis l'échéance, au moins 1.
    """

    jours_restants: int
    en_retard: bool

    def __post_init__(self) -> None:
        """Refuse un délai incohérent.

        Lève :
            ValeurInvalideError : le nombre de jours est négatif, ou le chantier est
                dit en retard sans avoir dépassé son échéance d'au moins un jour.
        """
        if self.jours_restants < 0:
            raise ValeurInvalideError("Un délai se compte en jours positifs ou nuls.")
        if self.en_retard and self.jours_restants < RETARD_MINIMAL:
            raise ValeurInvalideError("Un chantier en retard l'est d'au moins un jour.")


def calculer_delai(echeance: date, aujourd_hui: date) -> Delai:
    """Calcule le délai d'un chantier à la date du jour.

    Le chantier n'est en retard que le lendemain de son échéance : le jour même,
    il reste encore la journée pour terminer, et le délai vaut 0 jour restant.
    """
    ecart = (echeance - aujourd_hui).days
    return Delai(jours_restants=abs(ecart), en_retard=ecart < 0)
