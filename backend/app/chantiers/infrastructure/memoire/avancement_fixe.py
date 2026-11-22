"""Fournisseur d'avancement aux valeurs fixées par le test.

Il remplace le calcul du module étapes dans les tests de chantiers, qui n'ont pas
à connaître ce module.
"""

from collections.abc import Mapping, Sequence
from uuid import UUID


class AvancementFixe:
    """Implémentation de `FournisseurAvancement` qui renvoie des pourcentages connus d'avance.

    Un chantier absent des valeurs fixées est à 0 %, comme un chantier sans étape.
    """

    def __init__(self, pourcentages: Mapping[UUID, int]) -> None:
        self._pourcentages = pourcentages

    def executer(self, chantier_ids: Sequence[UUID]) -> Mapping[UUID, int]:
        """Renvoie le pourcentage fixé de chaque chantier demandé."""
        return {chantier_id: self._pourcentages.get(chantier_id, 0) for chantier_id in chantier_ids}
