"""Plafonds de volume des lectures du tableau de bord : « À valider » et fil d'activité.

Ce ne sont pas des règles métier : aucune règle du produit ne dit qu'un chef ne
peut avoir que 50 étapes à valider. Ce sont des choix techniques, qui bornent le
coût d'une lecture et la taille d'une réponse quelle que soit la demande. La
démonstration est publique et ouverte en écriture : sans plafond, n'importe qui
pourrait faire grossir sans limite ces lectures. Ils vivent donc dans la couche
application, à côté des cas d'usage qui les appliquent, et non dans le domaine.
"""

from dataclasses import dataclass

from app.shared.domain.erreurs import ValeurInvalideError

# Nombre maximal d'étapes de la liste « À valider ». Le chef traite d'abord les
# plus anciennement signalées : ce sont donc elles qui sont gardées, selon le tri
# du domaine (`trier_par_signalement`).
LIMITE_A_VALIDER = 50

# Bornes du nombre d'entrées du fil d'activité, et la valeur prise sans demande.
LIMITE_ACTIVITE_MIN = 1
LIMITE_ACTIVITE_MAX = 50
LIMITE_ACTIVITE_PAR_DEFAUT = 10


@dataclass(frozen=True, slots=True)
class LimiteActivite:
    """Nombre d'entrées demandées dans le fil d'activité, de 1 à 50 (10 par défaut).

    La limite vient de la requête : elle est validée à la construction, pour
    qu'une valeur hors des bornes ne puisse jamais atteindre le repository.
    """

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
