"""Cas d'usage : lister les derniers changements de statut des étapes."""

from dataclasses import dataclass

from app.etapes.application.ports import UnitOfWorkEtapes
from app.etapes.application.vues import ActiviteVue, vue_activite
from app.etapes.domain.activite import LIMITE_ACTIVITE_PAR_DEFAUT, LimiteActivite
from app.shared.domain.acteur import Acteur


@dataclass(frozen=True)
class DemandeActiviteRecente:
    """Demande du fil d'activité : `limite` est le nombre d'entrées voulues, de 1 à 50."""

    limite: int = LIMITE_ACTIVITE_PAR_DEFAUT


class ListerActiviteRecente:
    """Liste les dernières entrées d'historique, toutes étapes confondues.

    C'est le fil d'activité du tableau de bord, de la plus récente entrée à la plus
    ancienne. Il est ouvert aux deux profils : dans le squelette, chef et ouvrier
    voient tous les chantiers, donc toute leur activité (docs/plan/squelette.md).
    L'acteur est tout de même reçu, comme dans chaque cas d'usage : c'est par lui
    que passera le cloisonnement par chantier en phase 2. La limite est validée par
    le domaine avant toute lecture.

    Lève :
        ValeurInvalideError : la limite est hors des bornes de `LimiteActivite`.
    """

    def __init__(self, uow: UnitOfWorkEtapes) -> None:
        self._uow = uow

    def executer(self, demande: DemandeActiviteRecente, acteur: Acteur) -> tuple[ActiviteVue, ...]:
        """Renvoie les entrées du fil, de la plus récente à la plus ancienne."""
        limite = LimiteActivite(demande.limite)
        with self._uow:
            transitions = self._uow.etapes.lister_dernieres_transitions(limite.valeur)
            return tuple(vue_activite(etape, entree) for etape, entree in transitions)
