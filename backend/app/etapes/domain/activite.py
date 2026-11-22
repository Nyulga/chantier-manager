"""Objet valeur `LimiteActivite` : le nombre d'entrées du fil d'activité à afficher."""

from dataclasses import dataclass

from app.shared.domain.erreurs import ValeurInvalideError

# Le fil d'activité du tableau de bord montre les derniers changements. Le plafond
# borne le coût de la lecture et la taille de la réponse, quelle que soit la demande.
LIMITE_ACTIVITE_MIN = 1
LIMITE_ACTIVITE_MAX = 50
LIMITE_ACTIVITE_PAR_DEFAUT = 10


@dataclass(frozen=True, slots=True)
class LimiteActivite:
    """Nombre d'entrées demandées dans le fil d'activité, de 1 à 50 (10 par défaut)."""

    valeur: int = LIMITE_ACTIVITE_PAR_DEFAUT

    def __post_init__(self) -> None:
        """Refuse une limite hors des bornes.

        Lève :
            ValeurInvalideError : la limite est inférieure à 1 ou supérieure à 50.
        """
        if not LIMITE_ACTIVITE_MIN <= self.valeur <= LIMITE_ACTIVITE_MAX:
            raise ValeurInvalideError(
                f"Le fil d'activité compte de {LIMITE_ACTIVITE_MIN} "
                f"à {LIMITE_ACTIVITE_MAX} entrées."
            )
