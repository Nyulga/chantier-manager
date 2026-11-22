"""Cas d'usage : lister les chantiers, avec leur avancement."""

from app.chantiers.application.ports import FournisseurAvancement, UnitOfWorkChantiers
from app.chantiers.application.vues import ChantierVue, vue_chantier
from app.shared.domain.acteur import Acteur


class ListerChantiers:
    """Liste les chantiers, dans l'ordre de création, chacun avec son avancement.

    Dans le squelette, toute personne qui accède au site voit tous les chantiers :
    le cloisonnement par affectation est reporté à la phase 2
    (docs/plan/squelette.md). Le droit qui dépend du rôle, voir le budget, est
    appliqué par la vue.
    """

    def __init__(self, uow: UnitOfWorkChantiers, avancement: FournisseurAvancement) -> None:
        self._uow = uow
        self._avancement = avancement

    def executer(self, acteur: Acteur) -> tuple[ChantierVue, ...]:
        """Renvoie la vue de chaque chantier pour l'acteur.

        Les avancements sont demandés en une seule fois, pour tous les chantiers,
        afin d'éviter une lecture par chantier.
        """
        with self._uow:
            chantiers = self._uow.chantiers.lister()
            avancements = self._avancement.executer([chantier.id for chantier in chantiers])
            return tuple(
                vue_chantier(chantier, acteur, avancements[chantier.id]) for chantier in chantiers
            )
