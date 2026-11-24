"""Assemblage des cas d'usage d'étapes sur des fakes mémoire, comme le fera la composition root.

Les services publics de chantiers sont les vrais, branchés sur leur Unit of Work
mémoire : les tests vérifient ainsi l'intégration réelle entre les deux modules.
"""

from dataclasses import dataclass, field

from app.chantiers.application.autoriser_ajout_etape import AutoriserAjoutEtape
from app.chantiers.application.evaluer_creation_chantier import EvaluerCreationChantier
from app.chantiers.application.verifier_chantier_existe import VerifierChantierExiste
from app.chantiers.infrastructure.memoire.unit_of_work import MemoireUnitOfWorkChantiers
from app.etapes.application.ajouter_etape import AjouterEtape
from app.etapes.application.calculer_resumes_etapes import CalculerResumesEtapes
from app.etapes.application.changer_statut_etape import ChangerStatutEtape
from app.etapes.application.consulter_capacites import ConsulterCapacites
from app.etapes.application.lister_activite_recente import ListerActiviteRecente
from app.etapes.application.lister_etapes import ListerEtapes
from app.etapes.application.lister_etapes_a_valider import ListerEtapesAValider
from app.etapes.infrastructure.memoire.unit_of_work import MemoireUnitOfWorkEtapes
from app.shared.infrastructure.memoire.generateur_id_previsible import GenerateurIdPrevisible
from app.shared.infrastructure.memoire.horloge_fixe import HorlogeFixe
from tests.fabriques.chantiers import un_chantier
from tests.fabriques.etapes import ID_CHANTIER, INSTANT


def uow_chantiers_avec_un_chantier() -> MemoireUnitOfWorkChantiers:
    uow = MemoireUnitOfWorkChantiers()
    uow.chantiers.ajouter(un_chantier(ID_CHANTIER.int))
    return uow


@dataclass
class Contexte:
    uow: MemoireUnitOfWorkEtapes = field(default_factory=MemoireUnitOfWorkEtapes)
    chantiers: MemoireUnitOfWorkChantiers = field(default_factory=uow_chantiers_avec_un_chantier)

    def ajouter_etape(self) -> AjouterEtape:
        return AjouterEtape(self.uow, GenerateurIdPrevisible(), AutoriserAjoutEtape(self.chantiers))

    def lister_etapes(self) -> ListerEtapes:
        return ListerEtapes(self.uow, VerifierChantierExiste(self.chantiers))

    def changer_statut(self) -> ChangerStatutEtape:
        return ChangerStatutEtape(self.uow, HorlogeFixe(INSTANT))

    def calculer_resumes(self) -> CalculerResumesEtapes:
        return CalculerResumesEtapes(self.uow)

    def lister_etapes_a_valider(self) -> ListerEtapesAValider:
        return ListerEtapesAValider(self.uow)

    def lister_activite_recente(self) -> ListerActiviteRecente:
        return ListerActiviteRecente(self.uow)

    def consulter_capacites(self) -> ConsulterCapacites:
        return ConsulterCapacites(EvaluerCreationChantier())
