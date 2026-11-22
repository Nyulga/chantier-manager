"""Cas d'usage : consulter le détail d'un chantier."""

from uuid import UUID

from app.chantiers.application.ports import FournisseurResumeEtapes, UnitOfWorkChantiers
from app.chantiers.application.vues import ChantierVue, vue_chantier
from app.shared.application.ports import Horloge
from app.shared.domain.acteur import Acteur


class ConsulterChantier:
    """Renvoie le détail d'un chantier, avec le résumé de ses étapes et son délai.

    Comme pour la liste, tout chantier est visible dans le squelette ; la vue
    masque le budget à un ouvrier.

    Lève :
        NonTrouveError : le chantier n'existe pas.
    """

    def __init__(
        self, uow: UnitOfWorkChantiers, resumes: FournisseurResumeEtapes, horloge: Horloge
    ) -> None:
        self._uow = uow
        self._resumes = resumes
        self._horloge = horloge

    def executer(self, chantier_id: UUID, acteur: Acteur) -> ChantierVue:
        """Renvoie la vue du chantier pour l'acteur.

        Le résumé est demandé après la fermeture de la transaction des chantiers,
        car son calcul ouvre la sienne : la requête ne tient qu'une connexion à la fois.
        """
        with self._uow:
            chantier = self._uow.chantiers.obtenir(chantier_id)
        resumes = self._resumes.executer([chantier.id])
        aujourd_hui = self._horloge.aujourd_hui()
        return vue_chantier(chantier, acteur, resumes[chantier.id], aujourd_hui)
