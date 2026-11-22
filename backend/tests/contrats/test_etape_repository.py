"""Contrat du port `EtapeRepository` : joué sur le fake mémoire et sur SQL."""

import pytest

from app.etapes.application.ports import UnitOfWorkEtapes
from app.etapes.domain.cycle import ActionEtape, StatutEtape
from app.etapes.domain.etape import Etape
from app.shared.domain.acteur import Acteur, Role
from app.shared.domain.erreurs import NonTrouveError
from tests.contrats.conftest import AUTRE_CHANTIER
from tests.unitaires.etapes.fabriques import ID_CHANTIER, INSTANT, une_etape

OUVRIER = Acteur(Role.OUVRIER)
VERSION_APRES_UNE_TRANSITION = 2


def enregistrer(uow: UnitOfWorkEtapes, *etapes: Etape) -> None:
    with uow:
        for etape in etapes:
            uow.etapes.ajouter(etape)
        uow.valider()


def test_une_etape_valide_est_relue_identique_dans_une_autre_transaction(
    uow_etapes: UnitOfWorkEtapes,
) -> None:
    etape = une_etape()
    enregistrer(uow_etapes, etape)

    with uow_etapes:
        relue = uow_etapes.etapes.obtenir(etape.id)

    assert relue == etape


def test_une_etape_inconnue_leve_non_trouve(uow_etapes: UnitOfWorkEtapes) -> None:
    with uow_etapes, pytest.raises(NonTrouveError):
        uow_etapes.etapes.obtenir(une_etape().id)


def test_une_transition_validee_est_relue_avec_son_historique_et_sa_version(
    uow_etapes: UnitOfWorkEtapes,
) -> None:
    etape = une_etape()
    enregistrer(uow_etapes, etape)

    with uow_etapes:
        a_modifier = uow_etapes.etapes.obtenir(etape.id)
        a_modifier.appliquer(ActionEtape.DEMARRER, OUVRIER, INSTANT)
        uow_etapes.valider()
    with uow_etapes:
        relue = uow_etapes.etapes.obtenir(etape.id)

    assert relue.statut is StatutEtape.EN_COURS
    assert relue.version == VERSION_APRES_UNE_TRANSITION
    assert [(h.role, h.ancien_statut, h.nouveau_statut, h.date) for h in relue.historique] == [
        (Role.OUVRIER, StatutEtape.A_FAIRE, StatutEtape.EN_COURS, INSTANT)
    ]


def test_l_historique_est_relu_dans_l_ordre_des_transitions(uow_etapes: UnitOfWorkEtapes) -> None:
    etape = une_etape()
    enregistrer(uow_etapes, etape)

    for action in (ActionEtape.DEMARRER, ActionEtape.SIGNALER_TERMINEE):
        with uow_etapes:
            uow_etapes.etapes.obtenir(etape.id).appliquer(action, OUVRIER, INSTANT)
            uow_etapes.valider()
    with uow_etapes:
        relue = uow_etapes.etapes.obtenir(etape.id)

    assert [h.nouveau_statut for h in relue.historique] == [
        StatutEtape.EN_COURS,
        StatutEtape.TERMINEE_A_VALIDER,
    ]


def test_une_transition_non_validee_est_annulee(uow_etapes: UnitOfWorkEtapes) -> None:
    etape = une_etape()
    enregistrer(uow_etapes, etape)

    with uow_etapes:
        uow_etapes.etapes.obtenir(etape.id).appliquer(ActionEtape.DEMARRER, OUVRIER, INSTANT)
    with uow_etapes:
        relue = uow_etapes.etapes.obtenir(etape.id)

    assert (relue.statut, relue.version, relue.historique) == (StatutEtape.A_FAIRE, 1, [])


def test_les_etapes_d_un_chantier_sont_listees_par_ordre_sans_celles_des_autres(
    uow_etapes: UnitOfWorkEtapes,
) -> None:
    enregistrer(
        uow_etapes,
        une_etape(ordre=2),
        une_etape(ordre=1),
        une_etape(ordre=1, chantier_id=AUTRE_CHANTIER),
    )

    with uow_etapes:
        etapes = uow_etapes.etapes.lister_par_chantiers([ID_CHANTIER])

    assert [(etape.chantier_id, etape.ordre) for etape in etapes] == [
        (ID_CHANTIER, 1),
        (ID_CHANTIER, 2),
    ]


def test_aucun_chantier_demande_donne_une_liste_vide(uow_etapes: UnitOfWorkEtapes) -> None:
    enregistrer(uow_etapes, une_etape())

    with uow_etapes:
        etapes = uow_etapes.etapes.lister_par_chantiers([])

    assert etapes == []
