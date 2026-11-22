"""Contrat du port `EtapeRepository` : joué sur le fake mémoire et sur SQL."""

import pytest

from app.etapes.application.ports import UnitOfWorkEtapes
from app.etapes.domain.cycle import ActionEtape, StatutEtape
from app.etapes.domain.etape import Etape
from app.shared.domain.acteur import Acteur, Role
from app.shared.domain.erreurs import NonTrouveError
from tests.contrats.conftest import AUTRE_CHANTIER
from tests.unitaires.etapes.fabriques import (
    ID_CHANTIER,
    INSTANT,
    heures_apres,
    id_etape,
    une_etape,
    une_etape_signalee,
)

OUVRIER = Acteur(Role.OUVRIER)
VERSION_APRES_UNE_TRANSITION = 2
# Assez large pour ne rien couper : les tests de la limite en passent une plus petite.
LIMITE = 10


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


def test_les_etapes_a_valider_sont_listees_tous_chantiers_confondus(
    uow_etapes: UnitOfWorkEtapes,
) -> None:
    signalee = une_etape_signalee(heures_apres(1), ordre=1)
    signalee_ailleurs = une_etape_signalee(heures_apres(2), ordre=1, chantier_id=AUTRE_CHANTIER)
    enregistrer(
        uow_etapes,
        signalee,
        signalee_ailleurs,
        une_etape(ordre=2),
        une_etape(StatutEtape.VALIDEE, ordre=3),
    )

    with uow_etapes:
        etapes = uow_etapes.etapes.lister_a_valider(LIMITE)

    assert {etape.id for etape in etapes} == {signalee.id, signalee_ailleurs.id}


def test_une_etape_a_valider_garde_son_historique(uow_etapes: UnitOfWorkEtapes) -> None:
    signalee = une_etape_signalee(heures_apres(1))
    enregistrer(uow_etapes, signalee)

    with uow_etapes:
        [relue] = uow_etapes.etapes.lister_a_valider(LIMITE)

    assert relue.signalee_le() == heures_apres(1)


def test_aucune_etape_a_valider_donne_une_liste_vide(uow_etapes: UnitOfWorkEtapes) -> None:
    enregistrer(uow_etapes, une_etape(), une_etape(StatutEtape.VALIDEE, ordre=2))

    with uow_etapes:
        etapes = uow_etapes.etapes.lister_a_valider(LIMITE)

    assert etapes == []


def test_la_limite_garde_les_etapes_signalees_depuis_le_plus_longtemps(
    uow_etapes: UnitOfWorkEtapes,
) -> None:
    enregistrer(
        uow_etapes,
        une_etape_signalee(heures_apres(9), ordre=1),
        une_etape_signalee(heures_apres(3), ordre=2),
        une_etape_signalee(heures_apres(6), ordre=1, chantier_id=AUTRE_CHANTIER),
    )

    with uow_etapes:
        etapes = uow_etapes.etapes.lister_a_valider(2)

    assert {etape.id for etape in etapes} == {id_etape(2), id_etape(1, AUTRE_CHANTIER)}


def test_la_limite_compte_le_dernier_signalement_d_une_etape_refusee(
    uow_etapes: UnitOfWorkEtapes,
) -> None:
    resignalee = une_etape_signalee(heures_apres(1), ordre=1)
    resignalee.appliquer(ActionEtape.REFUSER, Acteur(Role.CHEF), heures_apres(2), "À reprendre")
    resignalee.appliquer(ActionEtape.SIGNALER_TERMINEE, OUVRIER, heures_apres(8))
    enregistrer(uow_etapes, resignalee, une_etape_signalee(heures_apres(5), ordre=2))

    with uow_etapes:
        etapes = uow_etapes.etapes.lister_a_valider(1)

    assert [etape.id for etape in etapes] == [id_etape(2)]


def test_a_signalement_egal_la_limite_garde_le_plus_petit_identifiant(
    uow_etapes: UnitOfWorkEtapes,
) -> None:
    enregistrer(
        uow_etapes,
        une_etape_signalee(heures_apres(4), ordre=2),
        une_etape_signalee(heures_apres(4), ordre=1),
    )

    with uow_etapes:
        etapes = uow_etapes.etapes.lister_a_valider(1)

    assert [etape.id for etape in etapes] == [id_etape(1)]


def test_la_limite_garde_d_abord_une_etape_a_valider_sans_signalement_connu(
    uow_etapes: UnitOfWorkEtapes,
) -> None:
    enregistrer(
        uow_etapes,
        une_etape_signalee(heures_apres(1), ordre=1),
        une_etape(StatutEtape.TERMINEE_A_VALIDER, ordre=2),
    )

    with uow_etapes:
        etapes = uow_etapes.etapes.lister_a_valider(1)

    assert [etape.id for etape in etapes] == [id_etape(2)]


def test_sans_historique_il_n_y_a_aucune_transition(uow_etapes: UnitOfWorkEtapes) -> None:
    enregistrer(uow_etapes, une_etape())

    with uow_etapes:
        transitions = uow_etapes.etapes.lister_dernieres_transitions(10)

    assert transitions == []


def test_les_transitions_vont_de_la_plus_recente_a_la_plus_ancienne(
    uow_etapes: UnitOfWorkEtapes,
) -> None:
    ancienne = une_etape_signalee(heures_apres(2), ordre=1)
    recente = une_etape_signalee(heures_apres(4), ordre=2, chantier_id=AUTRE_CHANTIER)
    enregistrer(uow_etapes, ancienne, recente)

    with uow_etapes:
        transitions = uow_etapes.etapes.lister_dernieres_transitions(10)

    assert [(etape.id, entree.date) for etape, entree in transitions] == [
        (recente.id, heures_apres(4)),
        (recente.id, heures_apres(3)),
        (ancienne.id, heures_apres(2)),
        (ancienne.id, heures_apres(1)),
    ]


def test_la_limite_ne_garde_que_les_transitions_les_plus_recentes(
    uow_etapes: UnitOfWorkEtapes,
) -> None:
    etape = une_etape_signalee(heures_apres(10))
    enregistrer(uow_etapes, etape)

    with uow_etapes:
        transitions = uow_etapes.etapes.lister_dernieres_transitions(1)

    assert [entree.nouveau_statut for _, entree in transitions] == [StatutEtape.TERMINEE_A_VALIDER]


def test_a_date_egale_la_transition_ajoutee_en_dernier_vient_en_premier(
    uow_etapes: UnitOfWorkEtapes,
) -> None:
    etape = une_etape()
    etape.appliquer(ActionEtape.DEMARRER, OUVRIER, INSTANT)
    etape.appliquer(ActionEtape.SIGNALER_TERMINEE, OUVRIER, INSTANT)
    enregistrer(uow_etapes, etape)

    with uow_etapes:
        transitions = uow_etapes.etapes.lister_dernieres_transitions(10)

    assert [entree.nouveau_statut for _, entree in transitions] == [
        StatutEtape.TERMINEE_A_VALIDER,
        StatutEtape.EN_COURS,
    ]


def test_une_transition_est_renvoyee_avec_son_etape_et_son_commentaire(
    uow_etapes: UnitOfWorkEtapes,
) -> None:
    etape = une_etape_signalee(heures_apres(1))
    etape.appliquer(ActionEtape.REFUSER, Acteur(Role.CHEF), heures_apres(2), "Joints à reprendre")
    enregistrer(uow_etapes, etape)

    with uow_etapes:
        [(etape_relue, entree), *_] = uow_etapes.etapes.lister_dernieres_transitions(10)

    assert (etape_relue.id, etape_relue.titre, entree.role, entree.commentaire) == (
        etape.id,
        etape.titre,
        Role.CHEF,
        "Joints à reprendre",
    )
