from datetime import date
from decimal import Decimal
from uuid import UUID

import pytest

from app.chantiers.application.creer_chantier import CreerChantier, NouveauChantier
from app.chantiers.application.vues import AdresseVue, ChantierVue
from app.chantiers.infrastructure.memoire.avancement_fixe import AvancementFixe
from app.chantiers.infrastructure.memoire.unit_of_work import MemoireUnitOfWorkChantiers
from app.shared.domain.acteur import Acteur, Role
from app.shared.domain.erreurs import AccesRefuseError, ValeurInvalideError
from app.shared.infrastructure.memoire.generateur_id_previsible import GenerateurIdPrevisible
from tests.unitaires.chantiers.fabriques import BUDGET, DEBUT, ECHEANCE, une_commande

CHEF = Acteur(Role.CHEF)
PREMIER_ID = UUID(int=1)
AVANCEMENT = 0


def un_service() -> tuple[CreerChantier, MemoireUnitOfWorkChantiers]:
    uow = MemoireUnitOfWorkChantiers()
    service = CreerChantier(uow, GenerateurIdPrevisible(), AvancementFixe({}))
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
        avancement=AVANCEMENT,
        peut_ajouter_etape=True,
    )


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
