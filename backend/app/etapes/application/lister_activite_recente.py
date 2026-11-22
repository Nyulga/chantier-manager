"""Cas d'usage : lister les derniers changements de statut des étapes."""

from dataclasses import dataclass

from app.etapes.application.plafonds import LIMITE_ACTIVITE_PAR_DEFAUT, LimiteActivite
from app.etapes.application.ports import UnitOfWorkEtapes
from app.etapes.application.vues import ActiviteVue, vue_activite
from app.etapes.domain.politiques import peut_consulter_activite
from app.shared.application.acces import exiger_acces
from app.shared.domain.acteur import Acteur


@dataclass(frozen=True)
class DemandeActiviteRecente:
    """Demande du fil d'activité : `limite` est le nombre d'entrées voulues, de 1 à 50."""

    limite: int = LIMITE_ACTIVITE_PAR_DEFAUT


class ListerActiviteRecente:
    """Liste les dernières entrées d'historique, toutes étapes confondues.

    C'est le fil d'activité du tableau de bord, de la plus récente entrée à la plus
    ancienne. Le droit est vérifié en premier, par la politique du domaine
    `peut_consulter_activite` : dans le squelette, elle l'ouvre aux deux profils,
    car chef et ouvrier voient tous les chantiers (docs/plan/squelette.md) ; en
    phase 2, c'est elle qui portera le cloisonnement par chantier. La limite est
    ensuite validée (`LimiteActivite`), avant toute lecture : c'est un plafond de
    volume, choisi pour borner le coût de la lecture, et non une règle métier.

    Lève :
        AccesRefuseError : la politique refuse le fil à l'acteur, ce qui n'arrive
            à aucun rôle du squelette. Ce n'est pas `NonTrouveError` : le fil n'est
            pas un objet dont il faudrait cacher l'existence.
        ValeurInvalideError : la limite est hors des bornes de `LimiteActivite`.
    """

    def __init__(self, uow: UnitOfWorkEtapes) -> None:
        self._uow = uow

    def executer(self, demande: DemandeActiviteRecente, acteur: Acteur) -> tuple[ActiviteVue, ...]:
        """Renvoie les entrées du fil, de la plus récente à la plus ancienne."""
        exiger_acces(
            autorise=peut_consulter_activite(acteur),
            message="Ce profil ne peut pas consulter le fil d'activité.",
        )
        limite = LimiteActivite(demande.limite)
        with self._uow:
            transitions = self._uow.etapes.lister_dernieres_transitions(limite.valeur)
            return tuple(vue_activite(etape, entree) for etape, entree in transitions)
