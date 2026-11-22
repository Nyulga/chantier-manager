"""Assemblage des cas d'usage d'étapes sur des fakes mémoire, comme le fera la composition root.

Les services publics de chantiers sont les vrais, branchés sur leur Unit of Work
mémoire : les tests vérifient ainsi l'intégration réelle entre les deux modules.
"""

from dataclasses import dataclass, field

from app.chantiers.application.autoriser_ajout_etape import AutoriserAjoutEtape
from app.chantiers.application.verifier_chantier_existe import VerifierChantierExiste
from app.chantiers.infrastructure.memoire.unit_of_work import MemoireUnitOfWorkChantiers
from app.etapes.application.ajouter_etape import AjouterEtape
from app.etapes.application.calculer_avancements import CalculerAvancements
from app.etapes.application.changer_statut_etape import ChangerStatutEtape
from app.etapes.application.lister_etapes import ListerEtapes
from app.etapes.infrastructure.memoire.unit_of_work import MemoireUnitOfWorkEtapes
from app.shared.infrastructure.memoire.generateur_id_previsible import GenerateurIdPrevisible
from app.shared.infrastructure.memoire.horloge_fixe import HorlogeFixe
from tests.unitaires.chantiers.fabriques import un_chantier
from tests.unitaires.etapes.fabriques import ID_CHANTIER, INSTANT


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

    def calculer_avancements(self) -> CalculerAvancements:
        return CalculerAvancements(self.uow)
