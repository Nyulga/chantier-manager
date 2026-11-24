"""Plafond du nombre d'étapes par chantier : 30, vérifié après le droit et l'existence."""

from uuid import UUID

import pytest

from app.etapes.application.ajouter_etape import NouvelleEtape
from app.etapes.application.plafonds import LIMITE_ETAPES_PAR_CHANTIER
from app.shared.application.erreurs import PlafondAtteintError
from app.shared.domain.acteur import Acteur, Role
from app.shared.domain.erreurs import AccesRefuseError
from tests.application.etapes.contexte import Contexte
from tests.fabriques.chantiers import un_chantier
from tests.fabriques.etapes import ID_CHANTIER, id_etape, une_etape

CHEF = Acteur(Role.CHEF)
AUTRE_CHANTIER = UUID(int=200)
# Plafond décidé par le propriétaire (journal du lot S6).
PLAFOND_DECIDE = 30


def un_contexte_avec(etapes: int, chantier_id: UUID = ID_CHANTIER) -> Contexte:
    """Contexte où le chantier donné compte déjà `etapes` étapes, d'ordres 1 à `etapes`."""
    contexte = Contexte()
    contexte.chantiers.chantiers.ajouter(un_chantier(AUTRE_CHANTIER.int))
    contexte.uow.etapes.elements = {
        id_etape(ordre, chantier_id): une_etape(ordre=ordre, chantier_id=chantier_id)
        for ordre in range(1, etapes + 1)
    }
    return contexte


def test_le_plafond_est_de_30_etapes_par_chantier() -> None:
    assert LIMITE_ETAPES_PAR_CHANTIER == PLAFOND_DECIDE


def test_la_derniere_etape_sous_le_plafond_est_ajoutee() -> None:
    contexte = un_contexte_avec(LIMITE_ETAPES_PAR_CHANTIER - 1)

    vue = contexte.ajouter_etape().executer(NouvelleEtape(ID_CHANTIER, "Finitions"), CHEF)

    assert (vue.ordre, contexte.uow.validations) == (LIMITE_ETAPES_PAR_CHANTIER, 1)


def test_au_plafond_l_ajout_est_refuse_sans_rien_ecrire() -> None:
    contexte = un_contexte_avec(LIMITE_ETAPES_PAR_CHANTIER)

    with pytest.raises(PlafondAtteintError) as erreur:
        contexte.ajouter_etape().executer(NouvelleEtape(ID_CHANTIER, "Finitions"), CHEF)

    assert str(erreur.value) == "Ce chantier a atteint sa limite de 30 étapes."
    assert len(contexte.uow.etapes.lister_par_chantiers([ID_CHANTIER])) == (
        LIMITE_ETAPES_PAR_CHANTIER
    )
    assert contexte.uow.validations == 0


def test_le_plafond_d_un_autre_chantier_ne_bloque_pas_celui_ci() -> None:
    contexte = un_contexte_avec(LIMITE_ETAPES_PAR_CHANTIER, chantier_id=AUTRE_CHANTIER)

    vue = contexte.ajouter_etape().executer(NouvelleEtape(ID_CHANTIER, "Finitions"), CHEF)

    assert (vue.ordre, contexte.uow.validations) == (1, 1)


def test_au_plafond_un_ouvrier_recoit_toujours_le_refus_de_droit() -> None:
    contexte = un_contexte_avec(LIMITE_ETAPES_PAR_CHANTIER)

    with pytest.raises(AccesRefuseError):
        contexte.ajouter_etape().executer(
            NouvelleEtape(ID_CHANTIER, "Finitions"), Acteur(Role.OUVRIER)
        )

    assert contexte.uow.validations == 0
