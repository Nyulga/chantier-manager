"""Objet valeur `Montant` : une somme d'argent en euros, toujours en `Decimal`.

L'argent n'est jamais un `float` : un `float` ne représente pas exactement les
centimes, et les arrondis s'accumulent (intent.md, §2.3).
"""

from dataclasses import dataclass
from decimal import Decimal

from app.shared.domain.erreurs import ValeurInvalideError

DEVISE = "EUR"
CENTIME = Decimal("0.01")
# Plus grande valeur que la colonne NUMERIC(12,2) peut enregistrer (ADR 0002).
MONTANT_MAX = Decimal("9999999999.99")


@dataclass(frozen=True, slots=True)
class Montant:
    """Somme d'argent positive ou nulle, au centime près, exprimée en euros (`DEVISE`).

    La précision est bornée au centime parce que la base stocke les montants en
    `NUMERIC(12,2)` (ADR 0002) : une valeur plus précise serait arrondie sans bruit
    à l'enregistrement, et le montant relu ne serait plus celui qui a été saisi.
    """

    valeur: Decimal

    def __post_init__(self) -> None:
        """Refuse toute valeur invalide, pour qu'un montant invalide ne puisse pas exister.

        Lève :
            ValeurInvalideError : la valeur n'est pas finie, est négative, dépasse `MONTANT_MAX`
                ou a plus de deux décimales.
        """
        # Le test de finitude passe en premier : comparer NaN à zéro lèverait une
        # erreur technique de `decimal` au lieu d'une erreur métier.
        if not self.valeur.is_finite():
            raise ValeurInvalideError("Le montant doit être un nombre.")
        if self.valeur < 0:
            raise ValeurInvalideError("Le montant ne peut pas être négatif.")
        # Le plafond est vérifié avant l'arrondi au centime, qui lèverait une erreur
        # technique de `decimal` sur une valeur trop grande.
        if self.valeur > MONTANT_MAX:
            raise ValeurInvalideError("Le montant dépasse la valeur maximale enregistrable.")
        if self.valeur != self.valeur.quantize(CENTIME):
            raise ValeurInvalideError("Le montant ne peut pas être plus précis que le centime.")
