"""Cas d'usage : annoncer ce que l'acteur peut faire depuis le tableau de bord."""

from app.etapes.application.ports import DroitCreationChantier
from app.etapes.application.vues import CapacitesVue
from app.etapes.domain.politiques import peut_lister_etapes_a_valider
from app.shared.domain.acteur import Acteur


class ConsulterCapacites:
    """Renvoie les capacités de l'acteur : son rôle et les actions générales permises.

    Le frontend affiche le lien « Nouveau chantier » et le bloc « À valider »
    d'après cette vue, sans jamais déduire un droit du profil (règle 02, vues).
    Chaque capacité est le résultat d'une politique du domaine : celle de
    chantiers, obtenue par le port `DroitCreationChantier`, et celle d'étapes. Le
    cas d'usage vit dans étapes, qui porte déjà le tableau de bord et peut
    s'appuyer sur chantiers ; l'inverse est interdit (contrat
    `chantiers-sans-etapes`).

    Il ne lit aucune donnée et n'ouvre aucune transaction : il n'y a rien à
    protéger, et tout acteur peut connaître ses propres capacités. Les cas d'usage
    concernés revérifient chacun leur droit.
    """

    def __init__(self, droit_creation: DroitCreationChantier) -> None:
        self._droit_creation = droit_creation

    def executer(self, acteur: Acteur) -> CapacitesVue:
        """Renvoie la vue des capacités de l'acteur."""
        return CapacitesVue(
            role=acteur.role.value,
            peut_creer_chantier=self._droit_creation.executer(acteur),
            peut_lister_etapes_a_valider=peut_lister_etapes_a_valider(acteur),
        )
