"""Contrat du port `UnitOfWork` : joué sur l'implémentation mémoire et sur SQL.

On l'observe au travers de la transaction d'étapes, qui porte un repository ; la
même sémantique vaut pour chaque module, dont la transaction hérite de la même
classe de base. Le dernier test le vérifie aussi sur la transaction de chantiers.
"""

import pytest

from app.chantiers.application.ports import UnitOfWorkChantiers
from app.etapes.application.changer_statut_etape import ChangementStatut, ChangerStatutEtape
from app.etapes.application.ports import UnitOfWorkEtapes
from app.etapes.domain.cycle import ActionEtape, StatutEtape
from app.shared.domain.acteur import Acteur, Role
from app.shared.domain.erreurs import ConflitVersionError, ValeurInvalideError
from app.shared.infrastructure.memoire.horloge_fixe import HorlogeFixe
from tests.unitaires.chantiers.fabriques import un_chantier
from tests.unitaires.etapes.fabriques import INSTANT, une_etape

OUVRIER = Acteur(Role.OUVRIER)
ETAPE = une_etape().id
# Un numéro de chantier que la fixture SQL n'a pas déjà enregistré.
CHANTIER_EN_PLUS = 7


def enregistrer_une_etape(uow: UnitOfWorkEtapes) -> None:
    with uow:
        uow.etapes.ajouter(une_etape())
        uow.valider()


def relire_l_etape(uow: UnitOfWorkEtapes) -> tuple[StatutEtape, int, int]:
    """Relit l'étape dans une nouvelle transaction : statut, version et taille de l'historique."""
    with uow:
        etape = uow.etapes.obtenir(ETAPE)
        return etape.statut, etape.version, len(etape.historique)


def test_ce_qui_est_valide_est_relu_dans_la_transaction_suivante(
    uow_etapes: UnitOfWorkEtapes,
) -> None:
    enregistrer_une_etape(uow_etapes)

    with uow_etapes:
        uow_etapes.etapes.obtenir(ETAPE).appliquer(ActionEtape.DEMARRER, OUVRIER, INSTANT)
        uow_etapes.valider()

    assert relire_l_etape(uow_etapes) == (StatutEtape.EN_COURS, 2, 1)


def test_sortir_sans_valider_annule_les_ecritures(uow_etapes: UnitOfWorkEtapes) -> None:
    enregistrer_une_etape(uow_etapes)

    with uow_etapes:
        uow_etapes.etapes.obtenir(ETAPE).appliquer(ActionEtape.DEMARRER, OUVRIER, INSTANT)

    assert relire_l_etape(uow_etapes) == (StatutEtape.A_FAIRE, 1, 0)


def test_une_exception_annule_les_ecritures_et_remonte(uow_etapes: UnitOfWorkEtapes) -> None:
    enregistrer_une_etape(uow_etapes)

    with pytest.raises(ValeurInvalideError), uow_etapes:
        uow_etapes.etapes.obtenir(ETAPE).appliquer(ActionEtape.DEMARRER, OUVRIER, INSTANT)
        raise ValeurInvalideError("Panne simulée au milieu de la transaction.")

    assert relire_l_etape(uow_etapes) == (StatutEtape.A_FAIRE, 1, 0)


def test_une_version_perimee_est_rejetee_sans_laisser_d_historique(
    uow_etapes: UnitOfWorkEtapes,
) -> None:
    enregistrer_une_etape(uow_etapes)
    changer = ChangerStatutEtape(uow_etapes, HorlogeFixe(INSTANT))
    changer.executer(ChangementStatut(ETAPE, "demarrer", version_attendue=1), OUVRIER)

    with pytest.raises(ConflitVersionError):
        changer.executer(ChangementStatut(ETAPE, "signaler_terminee", version_attendue=1), OUVRIER)

    assert relire_l_etape(uow_etapes) == (StatutEtape.EN_COURS, 2, 1)


def test_la_transaction_des_chantiers_annule_aussi_ce_qui_n_est_pas_valide(
    uow_chantiers: UnitOfWorkChantiers,
) -> None:
    with uow_chantiers:
        uow_chantiers.chantiers.ajouter(un_chantier(CHANTIER_EN_PLUS))

    with uow_chantiers:
        chantiers = uow_chantiers.chantiers.lister()

    assert chantiers == []
