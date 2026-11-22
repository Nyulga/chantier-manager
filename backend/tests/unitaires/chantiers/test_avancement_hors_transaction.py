from uuid import UUID

from app.chantiers.application.consulter_chantier import ConsulterChantier
from app.chantiers.application.lister_chantiers import ListerChantiers
from app.chantiers.infrastructure.memoire.unit_of_work import MemoireUnitOfWorkChantiers
from app.shared.domain.acteur import Acteur, Role
from tests.unitaires.chantiers.espions import AvancementEspion
from tests.unitaires.chantiers.fabriques import un_chantier

CHEF = Acteur(Role.CHEF)


def un_uow_avec_un_chantier() -> MemoireUnitOfWorkChantiers:
    uow = MemoireUnitOfWorkChantiers()
    uow.chantiers.ajouter(un_chantier(1))
    return uow


def test_lister_demande_l_avancement_apres_la_transaction() -> None:
    uow = un_uow_avec_un_chantier()
    espion = AvancementEspion(uow)

    ListerChantiers(uow, espion).executer(CHEF)

    assert espion.appele_en_transaction == [False]


def test_consulter_demande_l_avancement_apres_la_transaction() -> None:
    uow = un_uow_avec_un_chantier()
    espion = AvancementEspion(uow)

    ConsulterChantier(uow, espion).executer(UUID(int=1), CHEF)

    assert espion.appele_en_transaction == [False]
