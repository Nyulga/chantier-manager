"""Cas d'usage : lister les chantiers, avec le résumé de leurs étapes et leur délai."""

from app.chantiers.application.ports import FournisseurResumeEtapes, UnitOfWorkChantiers
from app.chantiers.application.vues import ChantierVue, vue_chantier
from app.shared.application.ports import Horloge
from app.shared.domain.acteur import Acteur


class ListerChantiers:
    """Liste les chantiers, dans l'ordre de création, chacun avec ses étapes et son délai.

    Dans le squelette, toute personne qui accède au site voit tous les chantiers :
    le cloisonnement par affectation est reporté à la phase 2
    (docs/plan/squelette.md). Le droit qui dépend du rôle, voir le budget, est
    appliqué par la vue.
    """

    def __init__(
        self, uow: UnitOfWorkChantiers, resumes: FournisseurResumeEtapes, horloge: Horloge
    ) -> None:
        self._uow = uow
        self._resumes = resumes
        self._horloge = horloge

    def executer(self, acteur: Acteur) -> tuple[ChantierVue, ...]:
        """Renvoie la vue de chaque chantier pour l'acteur.

        Les résumés sont demandés en une seule fois, pour tous les chantiers, afin
        d'éviter une lecture par chantier. Ils le sont après la fermeture de la
        transaction des chantiers, car leur calcul ouvre la sienne : une requête ne
        tient ainsi jamais deux connexions à la fois. La date du jour est lue une
        seule fois, pour que tous les délais de la liste soient comptés au même jour.
        """
        with self._uow:
            chantiers = self._uow.chantiers.lister()
        resumes = self._resumes.executer([chantier.id for chantier in chantiers])
        aujourd_hui = self._horloge.aujourd_hui()
        return tuple(
            vue_chantier(chantier, acteur, resumes[chantier.id], aujourd_hui)
            for chantier in chantiers
        )
