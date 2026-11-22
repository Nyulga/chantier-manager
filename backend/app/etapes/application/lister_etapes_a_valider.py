"""Cas d'usage : lister les étapes qui attendent la décision d'un chef."""

from app.etapes.application.ports import UnitOfWorkEtapes
from app.etapes.application.vues import EtapeAValiderVue, vue_etape_a_valider
from app.etapes.domain.cycle import StatutEtape
from app.etapes.domain.etape import trier_par_signalement
from app.etapes.domain.politiques import peut_lister_etapes_a_valider
from app.shared.domain.acteur import Acteur
from app.shared.domain.erreurs import AccesRefuseError


class ListerEtapesAValider:
    """Liste les étapes signalées terminées, tous chantiers confondus, pour un chef.

    C'est le bloc « À valider » du tableau de bord : les étapes y sont triées de la
    plus anciennement signalée à la plus récente, selon la règle du domaine. Dans
    le squelette, il couvre tous les chantiers ; en phase 2, seulement ceux du chef.
    Le droit est vérifié avant toute lecture : un ouvrier n'apprend rien des étapes.

    Lève :
        AccesRefuseError : l'acteur n'est pas chef. Ce n'est pas `NonTrouveError` :
            la file n'est pas un objet dont il faudrait cacher l'existence.
    """

    def __init__(self, uow: UnitOfWorkEtapes) -> None:
        self._uow = uow

    def executer(self, acteur: Acteur) -> tuple[EtapeAValiderVue, ...]:
        """Renvoie la vue de chaque étape à valider, avec les actions permises à l'acteur."""
        if not peut_lister_etapes_a_valider(acteur):
            raise AccesRefuseError("Seul un chef consulte les étapes à valider.")
        with self._uow:
            etapes = self._uow.etapes.lister_par_statut(StatutEtape.TERMINEE_A_VALIDER)
            return tuple(
                vue_etape_a_valider(etape, acteur) for etape in trier_par_signalement(etapes)
            )
