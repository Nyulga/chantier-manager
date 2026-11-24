"""Cas d'usage `CreerChantier` : droit du chef, invariants, vue et annulation."""

from datetime import UTC, date, datetime
from decimal import Decimal
from uuid import UUID

import pytest

from app.chantiers.application.creer_chantier import CreerChantier, NouveauChantier
from app.chantiers.application.vues import AdresseVue, ChantierVue
from app.chantiers.infrastructure.memoire.unit_of_work import MemoireUnitOfWorkChantiers
from app.shared.domain.acteur import Acteur, Role
from app.shared.domain.erreurs import AccesRefuseError, ValeurInvalideError
from app.shared.infrastructure.memoire.generateur_id_previsible import GenerateurIdPrevisible
from app.shared.infrastructure.memoire.horloge_fixe import HorlogeFixe
from tests.fabriques.chantiers import (
    BUDGET,
    DEBUT,
    ECHEANCE,
    JOURS_AVANT_ECHEANCE,
    LENDEMAIN_A_PARIS,
    MAINTENANT,
    une_commande,
)

CHEF = Acteur(Role.CHEF)
PREMIER_ID = UUID(int=1)
# Lendemain de l'échéance des fabriques (31 mars 2027).
LENDEMAIN_ECHEANCE = datetime(2027, 4, 1, 8, 0, tzinfo=UTC)


def un_service(
    maintenant: datetime = MAINTENANT,
) -> tuple[CreerChantier, MemoireUnitOfWorkChantiers]:
    uow = MemoireUnitOfWorkChantiers()
    service = CreerChantier(uow, GenerateurIdPrevisible(), HorlogeFixe(maintenant))
    return service, uow


def test_un_chef_cree_un_chantier_et_recoit_sa_vue_complete() -> None:
    service, _ = un_service()

    vue = service.executer(une_commande(), CHEF)

    assert vue == ChantierVue(
        id=PREMIER_ID,
        nom="Rénovation école",
        adresse=AdresseVue(voie="12 rue des Lilas", code_postal="69001", ville="Lyon"),
        client="Mairie fictive",
        date_debut=DEBUT,
        echeance=ECHEANCE,
        budget=BUDGET,
        avancement=0,
        etapes_validees=0,
        etapes_total=0,
        etapes_a_valider=0,
        jours_restants=JOURS_AVANT_ECHEANCE,
        en_retard=False,
        peut_ajouter_etape=True,
    )


@pytest.mark.parametrize(
    "maintenant", [LENDEMAIN_ECHEANCE, LENDEMAIN_A_PARIS], ids=["lendemain", "lendemain-a-paris"]
)
def test_un_chantier_cree_apres_son_echeance_est_aussitot_en_retard(maintenant: datetime) -> None:
    service, _ = un_service(maintenant)

    vue = service.executer(une_commande(), CHEF)

    assert (vue.jours_restants, vue.en_retard) == (1, True)


def test_le_chantier_cree_est_enregistre_dans_une_seule_transaction_validee() -> None:
    service, uow = un_service()

    service.executer(une_commande(), CHEF)

    assert uow.chantiers.obtenir(PREMIER_ID).nom == "Rénovation école"
    assert uow.validations == 1


def test_un_ouvrier_ne_peut_pas_creer_de_chantier() -> None:
    service, uow = un_service()

    with pytest.raises(AccesRefuseError):
        service.executer(une_commande(), Acteur(Role.OUVRIER))

    assert (uow.chantiers.lister(), uow.validations) == ([], 0)


@pytest.mark.parametrize(
    "commande",
    [
        une_commande(nom=" "),
        une_commande(ville=""),
        une_commande(budget=Decimal("-1")),
        une_commande(date_debut=date(2027, 1, 2), echeance=date(2027, 1, 1)),
    ],
)
def test_une_commande_invalide_n_enregistre_rien(commande: NouveauChantier) -> None:
    service, uow = un_service()

    with pytest.raises(ValeurInvalideError):
        service.executer(commande, CHEF)

    assert (uow.chantiers.lister(), uow.validations) == ([], 0)
