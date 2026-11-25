"""Propriétés de la machine à états et du résumé des étapes, vérifiées par hypothesis."""

import pytest
from hypothesis import given
from hypothesis import strategies as st

from app.etapes.domain.avancement import POURCENTAGE_MAX, resumer_etapes
from app.etapes.domain.cycle import ActionEtape, StatutEtape
from app.etapes.domain.etape import Etape
from app.shared.domain.acteur import Acteur, Role
from app.shared.domain.erreurs import AccesRefuseError, ErreurMetierError
from tests.fabriques.etapes import INSTANT, une_etape

Coup = tuple[ActionEtape, Role, str | None]

coups = st.tuples(
    st.sampled_from(ActionEtape),
    st.sampled_from(Role),
    st.none() | st.sampled_from(["", " ", "Reprendre l'enduit."]),
)
coups_d_ouvrier = st.tuples(st.sampled_from(ActionEtape), st.just(Role.OUVRIER), st.none())


def jouer(etape: Etape, coup: Coup) -> bool:
    """Applique un coup et dit s'il a réussi ; un refus métier laisse l'étape intacte."""
    action, role, commentaire = coup
    try:
        etape.appliquer(action, Acteur(role), INSTANT, commentaire)
    except ErreurMetierError:
        return False
    return True


def jouer_partie(etape: Etape, partie: list[Coup]) -> int:
    """Joue tous les coups dans l'ordre et renvoie le nombre de transitions réussies."""
    return sum(jouer(etape, coup) for coup in partie)


@given(st.lists(coups_d_ouvrier, max_size=30))
def test_aucune_suite_d_actions_d_ouvrier_n_atteint_validee(partie: list[Coup]) -> None:
    etape = une_etape()

    jouer_partie(etape, partie)

    assert etape.statut is not StatutEtape.VALIDEE


@given(st.lists(coups, max_size=30), st.sampled_from([ActionEtape.VALIDER, ActionEtape.REFUSER]))
def test_depuis_tout_etat_atteint_valider_ou_refuser_est_un_refus_de_droit_pour_l_ouvrier(
    partie: list[Coup], action: ActionEtape
) -> None:
    etape = une_etape()
    jouer_partie(etape, partie)

    with pytest.raises(AccesRefuseError):
        etape.appliquer(action, Acteur(Role.OUVRIER), INSTANT, "Reprendre l'enduit.")


@given(st.lists(coups, max_size=30))
def test_toute_entree_validee_de_l_historique_vient_d_un_chef(partie: list[Coup]) -> None:
    etape = une_etape()

    jouer_partie(etape, partie)

    roles_ayant_valide = {
        entree.role for entree in etape.historique if entree.nouveau_statut is StatutEtape.VALIDEE
    }
    assert roles_ayant_valide <= {Role.CHEF}


@given(st.lists(coups, max_size=30))
def test_chaque_transition_reussie_ajoute_exactement_une_entree(partie: list[Coup]) -> None:
    etape = une_etape()

    reussites = jouer_partie(etape, partie)

    assert len(etape.historique) == reussites
    assert etape.version == 1 + reussites


@given(st.lists(coups, max_size=30))
def test_l_historique_forme_une_chaine_continue_de_statuts(partie: list[Coup]) -> None:
    etape = une_etape()

    jouer_partie(etape, partie)

    departs = [entree.ancien_statut for entree in etape.historique]
    arrivees = [StatutEtape.A_FAIRE] + [entree.nouveau_statut for entree in etape.historique]
    assert departs == arrivees[:-1]
    assert arrivees[-1] is etape.statut


@given(st.lists(st.sampled_from(StatutEtape), max_size=50))
def test_l_avancement_reste_entre_0_et_100(statuts: list[StatutEtape]) -> None:
    etapes = [une_etape(statut, ordre) for ordre, statut in enumerate(statuts, start=1)]

    assert 0 <= resumer_etapes(etapes).avancement <= POURCENTAGE_MAX


@given(st.lists(st.sampled_from(StatutEtape), max_size=50))
def test_les_validees_et_les_a_valider_n_excedent_jamais_le_total(
    statuts: list[StatutEtape],
) -> None:
    etapes = [une_etape(statut, ordre) for ordre, statut in enumerate(statuts, start=1)]

    resume = resumer_etapes(etapes)

    assert resume.validees + resume.a_valider <= resume.total == len(statuts)
