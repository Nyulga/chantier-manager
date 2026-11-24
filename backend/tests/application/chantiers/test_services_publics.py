"""Cas d'usage publics de chantiers, utilisés par le module étapes."""

from uuid import UUID

import pytest

from app.chantiers.application.autoriser_ajout_etape import AutoriserAjoutEtape
from app.chantiers.application.evaluer_creation_chantier import EvaluerCreationChantier
from app.chantiers.application.verifier_chantier_existe import VerifierChantierExiste
from app.chantiers.infrastructure.memoire.unit_of_work import MemoireUnitOfWorkChantiers
from app.shared.domain.acteur import Acteur, Role
from app.shared.domain.erreurs import AccesRefuseError, NonTrouveError
from tests.fabriques.chantiers import un_chantier

CHEF = Acteur(Role.CHEF)
OUVRIER = Acteur(Role.OUVRIER)
CONNU = UUID(int=1)
INCONNU = UUID(int=99)


def un_uow() -> MemoireUnitOfWorkChantiers:
    uow = MemoireUnitOfWorkChantiers()
    uow.chantiers.ajouter(un_chantier(1))
    return uow


def test_verifier_un_chantier_existant_ne_leve_rien() -> None:
    VerifierChantierExiste(un_uow()).executer(CONNU)


def test_verifier_un_chantier_inconnu_leve_non_trouve() -> None:
    with pytest.raises(NonTrouveError):
        VerifierChantierExiste(un_uow()).executer(INCONNU)


def test_un_chef_peut_ajouter_une_etape_a_un_chantier_existant() -> None:
    AutoriserAjoutEtape(un_uow()).executer(CONNU, CHEF)


def test_un_ouvrier_ne_peut_pas_ajouter_d_etape() -> None:
    with pytest.raises(AccesRefuseError):
        AutoriserAjoutEtape(un_uow()).executer(CONNU, OUVRIER)


@pytest.mark.parametrize("acteur", [CHEF, OUVRIER])
def test_ajouter_une_etape_a_un_chantier_inconnu_leve_non_trouve(acteur: Acteur) -> None:
    with pytest.raises(NonTrouveError):
        AutoriserAjoutEtape(un_uow()).executer(INCONNU, acteur)


@pytest.mark.parametrize(("acteur", "attendu"), [(CHEF, True), (OUVRIER, False)])
def test_evaluer_la_creation_d_un_chantier_suit_la_politique_du_role(
    acteur: Acteur, attendu: bool
) -> None:
    assert EvaluerCreationChantier().executer(acteur) is attendu
