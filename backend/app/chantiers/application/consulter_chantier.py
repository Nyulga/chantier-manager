"""Cas d'usage : consulter le détail d'un chantier."""

from uuid import UUID

from app.chantiers.application.ports import FournisseurAvancement, UnitOfWorkChantiers
from app.chantiers.application.vues import ChantierVue, vue_chantier
from app.shared.domain.acteur import Acteur


class ConsulterChantier:
    """Renvoie le détail d'un chantier, avec son avancement.

    Comme pour la liste, tout chantier est visible dans le squelette ; la vue
    masque le budget à un ouvrier.

    Lève :
        NonTrouveError : le chantier n'existe pas.
    """

    def __init__(self, uow: UnitOfWorkChantiers, avancement: FournisseurAvancement) -> None:
        self._uow = uow
        self._avancement = avancement

    def executer(self, chantier_id: UUID, acteur: Acteur) -> ChantierVue:
        """Renvoie la vue du chantier pour l'acteur."""
        with self._uow:
            chantier = self._uow.chantiers.obtenir(chantier_id)
            avancements = self._avancement.executer([chantier.id])
            return vue_chantier(chantier, acteur, avancements[chantier.id])
