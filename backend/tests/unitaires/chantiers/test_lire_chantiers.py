"""Cas d'usage de lecture des chantiers : liste et détail, budget masqué, délai."""

from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID

import pytest

from app.chantiers.application.consulter_chantier import ConsulterChantier
from app.chantiers.application.lister_chantiers import ListerChantiers
from app.chantiers.application.ports import ResumeEtapesChantier
from app.chantiers.infrastructure.memoire.resume_etapes_fixe import ResumeEtapesFixe
from app.chantiers.infrastructure.memoire.unit_of_work import MemoireUnitOfWorkChantiers
from app.shared.domain.acteur import Acteur, Role
from app.shared.domain.erreurs import NonTrouveError
from app.shared.infrastructure.memoire.horloge_fixe import HorlogeFixe
from tests.unitaires.chantiers.fabriques import (
    BUDGET,
    JOURS_AVANT_ECHEANCE,
    LENDEMAIN_A_PARIS,
    MAINTENANT,
    un_chantier,
)

CHEF = Acteur(Role.CHEF)
OUVRIER = Acteur(Role.OUVRIER)
RESUMES = {
    UUID(int=1): ResumeEtapesChantier(avancement=25, validees=1, total=4, a_valider=2),
    UUID(int=2): ResumeEtapesChantier(avancement=100, validees=3, total=3, a_valider=0),
}
# Trois jours après l'échéance du 31 mars 2027, tard le soir à Paris (21 h 30 UTC, 23 h 30
# à Paris) : la date du jour reste le 3 avril.
TROIS_JOURS_APRES_ECHEANCE = datetime(2027, 4, 3, 21, 30, tzinfo=UTC)
JOURS_DE_RETARD = 3


def un_uow_avec_deux_chantiers() -> MemoireUnitOfWorkChantiers:
    uow = MemoireUnitOfWorkChantiers()
    uow.chantiers.ajouter(un_chantier(2, nom="Extension gymnase"))
    uow.chantiers.ajouter(un_chantier(1, nom="Rénovation école"))
    return uow


def une_liste(maintenant: datetime = MAINTENANT) -> ListerChantiers:
    return ListerChantiers(
        un_uow_avec_deux_chantiers(), ResumeEtapesFixe(RESUMES), HorlogeFixe(maintenant)
    )


def une_consultation(maintenant: datetime = MAINTENANT) -> ConsulterChantier:
    return ConsulterChantier(
        un_uow_avec_deux_chantiers(), ResumeEtapesFixe(RESUMES), HorlogeFixe(maintenant)
    )


def test_la_liste_suit_l_ordre_de_creation_et_porte_le_resume_de_chaque_chantier() -> None:
    vues = une_liste().executer(CHEF)

    assert [
        (vue.nom, vue.avancement, vue.etapes_validees, vue.etapes_total, vue.etapes_a_valider)
        for vue in vues
    ] == [
        ("Rénovation école", 25, 1, 4, 2),
        ("Extension gymnase", 100, 3, 3, 0),
    ]


def test_un_chantier_sans_resume_fourni_a_des_compteurs_nuls() -> None:
    service = ListerChantiers(
        un_uow_avec_deux_chantiers(), ResumeEtapesFixe({}), HorlogeFixe(MAINTENANT)
    )

    vues = service.executer(CHEF)

    assert {
        (vue.avancement, vue.etapes_validees, vue.etapes_total, vue.etapes_a_valider)
        for vue in vues
    } == {(0, 0, 0, 0)}


def test_sans_chantier_la_liste_est_vide() -> None:
    service = ListerChantiers(
        MemoireUnitOfWorkChantiers(), ResumeEtapesFixe({}), HorlogeFixe(MAINTENANT)
    )

    assert service.executer(CHEF) == ()


@pytest.mark.parametrize(
    ("maintenant", "jours_restants", "en_retard"),
    [
        (MAINTENANT, JOURS_AVANT_ECHEANCE, False),
        (TROIS_JOURS_APRES_ECHEANCE, JOURS_DE_RETARD, True),
        (LENDEMAIN_A_PARIS, 1, True),
    ],
    ids=["avant-echeance", "en-retard", "lendemain-a-paris"],
)
def test_la_liste_porte_le_delai_de_chaque_chantier_a_la_date_de_l_horloge(
    maintenant: datetime, jours_restants: int, en_retard: bool
) -> None:
    vues = une_liste(maintenant).executer(OUVRIER)

    assert {(vue.jours_restants, vue.en_retard) for vue in vues} == {(jours_restants, en_retard)}


@pytest.mark.parametrize(
    ("acteur", "budget", "peut_ajouter_etape"),
    [(CHEF, BUDGET, True), (OUVRIER, None, False)],
)
def test_la_liste_masque_le_budget_et_les_actions_de_chef_a_un_ouvrier(
    acteur: Acteur, budget: Decimal | None, peut_ajouter_etape: bool
) -> None:
    vues = une_liste().executer(acteur)

    assert {(vue.budget, vue.peut_ajouter_etape) for vue in vues} == {(budget, peut_ajouter_etape)}


@pytest.mark.parametrize(
    ("acteur", "budget", "peut_ajouter_etape"),
    [(CHEF, BUDGET, True), (OUVRIER, None, False)],
)
def test_consulter_un_chantier_renvoie_sa_vue_selon_le_role(
    acteur: Acteur, budget: Decimal | None, peut_ajouter_etape: bool
) -> None:
    vue = une_consultation().executer(UUID(int=2), acteur)

    assert (vue.nom, vue.avancement, vue.budget, vue.peut_ajouter_etape) == (
        "Extension gymnase",
        100,
        budget,
        peut_ajouter_etape,
    )


def test_consulter_un_chantier_renvoie_son_resume_et_son_delai() -> None:
    vue = une_consultation(TROIS_JOURS_APRES_ECHEANCE).executer(UUID(int=1), CHEF)

    assert (
        vue.etapes_validees,
        vue.etapes_total,
        vue.etapes_a_valider,
        vue.jours_restants,
        vue.en_retard,
    ) == (1, 4, 2, JOURS_DE_RETARD, True)


@pytest.mark.parametrize("acteur", [CHEF, OUVRIER])
def test_consulter_un_chantier_inconnu_leve_non_trouve(acteur: Acteur) -> None:
    with pytest.raises(NonTrouveError):
        une_consultation().executer(UUID(int=99), acteur)


def test_consulter_un_chantier_compte_le_delai_a_la_date_de_paris() -> None:
    vue = une_consultation(LENDEMAIN_A_PARIS).executer(UUID(int=1), CHEF)

    assert (vue.jours_restants, vue.en_retard) == (1, True)
