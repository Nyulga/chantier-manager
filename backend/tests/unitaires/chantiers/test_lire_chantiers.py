from decimal import Decimal
from uuid import UUID

import pytest

from app.chantiers.application.consulter_chantier import ConsulterChantier
from app.chantiers.application.lister_chantiers import ListerChantiers
from app.chantiers.infrastructure.memoire.avancement_fixe import AvancementFixe
from app.chantiers.infrastructure.memoire.unit_of_work import MemoireUnitOfWorkChantiers
from app.shared.domain.acteur import Acteur, Role
from app.shared.domain.erreurs import NonTrouveError
from tests.unitaires.chantiers.fabriques import BUDGET, un_chantier

CHEF = Acteur(Role.CHEF)
OUVRIER = Acteur(Role.OUVRIER)
AVANCEMENTS = {UUID(int=1): 25, UUID(int=2): 100}


def un_uow_avec_deux_chantiers() -> MemoireUnitOfWorkChantiers:
    uow = MemoireUnitOfWorkChantiers()
    uow.chantiers.ajouter(un_chantier(2, nom="Extension gymnase"))
    uow.chantiers.ajouter(un_chantier(1, nom="Rénovation école"))
    return uow


def test_la_liste_suit_l_ordre_de_creation_et_porte_l_avancement_de_chaque_chantier() -> None:
    service = ListerChantiers(un_uow_avec_deux_chantiers(), AvancementFixe(AVANCEMENTS))

    vues = service.executer(CHEF)

    assert [(vue.nom, vue.avancement) for vue in vues] == [
        ("Rénovation école", 25),
        ("Extension gymnase", 100),
    ]


def test_sans_chantier_la_liste_est_vide() -> None:
    service = ListerChantiers(MemoireUnitOfWorkChantiers(), AvancementFixe({}))

    assert service.executer(CHEF) == ()


@pytest.mark.parametrize(
    ("acteur", "budget", "peut_ajouter_etape"),
    [(CHEF, BUDGET, True), (OUVRIER, None, False)],
)
def test_la_liste_masque_le_budget_et_les_actions_de_chef_a_un_ouvrier(
    acteur: Acteur, budget: Decimal | None, peut_ajouter_etape: bool
) -> None:
    service = ListerChantiers(un_uow_avec_deux_chantiers(), AvancementFixe(AVANCEMENTS))

    vues = service.executer(acteur)

    assert {(vue.budget, vue.peut_ajouter_etape) for vue in vues} == {(budget, peut_ajouter_etape)}


@pytest.mark.parametrize(
    ("acteur", "budget", "peut_ajouter_etape"),
    [(CHEF, BUDGET, True), (OUVRIER, None, False)],
)
def test_consulter_un_chantier_renvoie_sa_vue_selon_le_role(
    acteur: Acteur, budget: Decimal | None, peut_ajouter_etape: bool
) -> None:
    service = ConsulterChantier(un_uow_avec_deux_chantiers(), AvancementFixe(AVANCEMENTS))

    vue = service.executer(UUID(int=2), acteur)

    assert (vue.nom, vue.avancement, vue.budget, vue.peut_ajouter_etape) == (
        "Extension gymnase",
        100,
        budget,
        peut_ajouter_etape,
    )


@pytest.mark.parametrize("acteur", [CHEF, OUVRIER])
def test_consulter_un_chantier_inconnu_leve_non_trouve(acteur: Acteur) -> None:
    service = ConsulterChantier(un_uow_avec_deux_chantiers(), AvancementFixe({}))

    with pytest.raises(NonTrouveError):
        service.executer(UUID(int=99), acteur)
