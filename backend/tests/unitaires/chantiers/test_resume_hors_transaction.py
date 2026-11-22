from uuid import UUID

from app.chantiers.application.consulter_chantier import ConsulterChantier
from app.chantiers.application.lister_chantiers import ListerChantiers
from app.chantiers.infrastructure.memoire.unit_of_work import MemoireUnitOfWorkChantiers
from app.shared.domain.acteur import Acteur, Role
from app.shared.infrastructure.memoire.horloge_fixe import HorlogeFixe
from tests.unitaires.chantiers.espions import ResumeEtapesEspion
from tests.unitaires.chantiers.fabriques import MAINTENANT, un_chantier

CHEF = Acteur(Role.CHEF)


def un_uow_avec_un_chantier() -> MemoireUnitOfWorkChantiers:
    uow = MemoireUnitOfWorkChantiers()
    uow.chantiers.ajouter(un_chantier(1))
    return uow


def test_lister_demande_le_resume_apres_la_transaction() -> None:
    uow = un_uow_avec_un_chantier()
    espion = ResumeEtapesEspion(uow)

    ListerChantiers(uow, espion, HorlogeFixe(MAINTENANT)).executer(CHEF)

    assert espion.appele_en_transaction == [False]


def test_consulter_demande_le_resume_apres_la_transaction() -> None:
    uow = un_uow_avec_un_chantier()
    espion = ResumeEtapesEspion(uow)

    ConsulterChantier(uow, espion, HorlogeFixe(MAINTENANT)).executer(UUID(int=1), CHEF)

    assert espion.appele_en_transaction == [False]
