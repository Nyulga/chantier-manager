"""Plafond du nombre de chantiers de la démo : 100 en tout, vérifié après le droit."""

import pytest

from app.chantiers.application.creer_chantier import CreerChantier
from app.chantiers.application.plafonds import LIMITE_CHANTIERS
from app.chantiers.infrastructure.memoire.unit_of_work import MemoireUnitOfWorkChantiers
from app.shared.application.erreurs import PlafondAtteintError
from app.shared.domain.acteur import Acteur, Role
from app.shared.domain.erreurs import AccesRefuseError
from app.shared.infrastructure.memoire.generateur_id_previsible import GenerateurIdPrevisible
from app.shared.infrastructure.memoire.horloge_fixe import HorlogeFixe
from tests.fabriques.chantiers import MAINTENANT, un_chantier, une_commande

CHEF = Acteur(Role.CHEF)
# Les chantiers déjà présents sont numérotés à partir d'ici, loin des identifiants 1, 2…
# que le générateur prévisible attribue aux nouveaux : aucun ne peut en écraser un autre.
PREMIER_NUMERO_EXISTANT = 1000
# Plafond décidé par le propriétaire (journal du lot S6).
PLAFOND_DECIDE = 100


def un_service_avec(existants: int) -> tuple[CreerChantier, MemoireUnitOfWorkChantiers]:
    """Service de création, sur une base qui compte déjà `existants` chantiers."""
    uow = MemoireUnitOfWorkChantiers()
    uow.chantiers.elements = {
        chantier.id: chantier
        for chantier in map(
            un_chantier, range(PREMIER_NUMERO_EXISTANT, PREMIER_NUMERO_EXISTANT + existants)
        )
    }
    return CreerChantier(uow, GenerateurIdPrevisible(), HorlogeFixe(MAINTENANT)), uow


def test_le_plafond_de_la_demo_est_de_100_chantiers() -> None:
    assert LIMITE_CHANTIERS == PLAFOND_DECIDE


def test_le_dernier_chantier_sous_le_plafond_est_cree() -> None:
    service, uow = un_service_avec(LIMITE_CHANTIERS - 1)

    service.executer(une_commande(), CHEF)

    assert (len(uow.chantiers.lister()), uow.validations) == (LIMITE_CHANTIERS, 1)


def test_au_plafond_la_creation_est_refusee_sans_rien_ecrire() -> None:
    service, uow = un_service_avec(LIMITE_CHANTIERS)

    with pytest.raises(PlafondAtteintError) as erreur:
        service.executer(une_commande(), CHEF)

    assert str(erreur.value) == "La démo a atteint sa limite de 100 chantiers."
    assert (len(uow.chantiers.lister()), uow.validations) == (LIMITE_CHANTIERS, 0)


def test_au_plafond_un_ouvrier_recoit_toujours_le_refus_de_droit() -> None:
    service, uow = un_service_avec(LIMITE_CHANTIERS)

    with pytest.raises(AccesRefuseError):
        service.executer(une_commande(), Acteur(Role.OUVRIER))

    assert uow.validations == 0
