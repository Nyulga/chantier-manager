"""Cas d'usage `ListerActiviteRecente` : fil d'activité borné, du plus récent au plus ancien."""

from uuid import UUID

import pytest

from app.etapes.application.lister_activite_recente import DemandeActiviteRecente
from app.etapes.application.vues import ActiviteVue
from app.etapes.domain.cycle import ActionEtape
from app.shared.domain.acteur import Acteur, Role
from app.shared.domain.erreurs import ValeurInvalideError
from tests.unitaires.etapes.contexte import Contexte
from tests.unitaires.etapes.fabriques import (
    ID_CHANTIER,
    heures_apres,
    id_etape,
    une_etape,
    une_etape_signalee,
)

CHEF = Acteur(Role.CHEF)
OUVRIER = Acteur(Role.OUVRIER)
AUTRE_CHANTIER = UUID(int=200)
LIMITE_PAR_DEFAUT = 10
# Six étapes signalées font douze transitions : plus que la limite par défaut.
ETAPES_SIGNALEES = 6


def un_contexte_avec_de_l_activite() -> Contexte:
    """Deux étapes de deux chantiers, dont les transitions s'entrecroisent dans le temps.

    Étape A (ce chantier) : démarrée à 0 h, signalée à 1 h, refusée à 4 h.
    Étape B (autre chantier) : démarrée à 2 h, signalée à 3 h.
    """
    contexte = Contexte()
    etape_a = une_etape_signalee(heures_apres(1), ordre=1)
    etape_a.appliquer(ActionEtape.REFUSER, CHEF, heures_apres(4), "Joints à reprendre.")
    contexte.uow.etapes.ajouter(etape_a)
    contexte.uow.etapes.ajouter(
        une_etape_signalee(heures_apres(3), ordre=1, chantier_id=AUTRE_CHANTIER)
    )
    return contexte


def un_contexte_avec_douze_transitions() -> Contexte:
    contexte = Contexte()
    for ordre in range(1, ETAPES_SIGNALEES + 1):
        contexte.uow.etapes.ajouter(une_etape_signalee(heures_apres(ordre * 2), ordre=ordre))
    return contexte


@pytest.mark.parametrize("acteur", [CHEF, OUVRIER])
def test_l_activite_va_de_la_plus_recente_a_la_plus_ancienne_pour_les_deux_profils(
    acteur: Acteur,
) -> None:
    contexte = un_contexte_avec_de_l_activite()

    vues = contexte.lister_activite_recente().executer(DemandeActiviteRecente(), acteur)

    assert [(vue.etape_id, vue.date) for vue in vues] == [
        (id_etape(1), heures_apres(4)),
        (id_etape(1, AUTRE_CHANTIER), heures_apres(3)),
        (id_etape(1, AUTRE_CHANTIER), heures_apres(2)),
        (id_etape(1), heures_apres(1)),
        (id_etape(1), heures_apres(0)),
    ]


def test_chaque_entree_decrit_la_transition_et_son_etape() -> None:
    contexte = un_contexte_avec_de_l_activite()

    vues = contexte.lister_activite_recente().executer(DemandeActiviteRecente(limite=1), CHEF)

    assert vues == (
        ActiviteVue(
            etape_id=id_etape(1),
            chantier_id=ID_CHANTIER,
            titre_etape="Gros œuvre",
            role="chef",
            ancien_statut="terminee_a_valider",
            nouveau_statut="en_cours",
            date=heures_apres(4),
            commentaire="Joints à reprendre.",
        ),
    )


def test_la_limite_garde_les_entrees_les_plus_recentes() -> None:
    contexte = un_contexte_avec_de_l_activite()

    vues = contexte.lister_activite_recente().executer(DemandeActiviteRecente(limite=2), CHEF)

    assert [vue.date for vue in vues] == [heures_apres(4), heures_apres(3)]


def test_par_defaut_l_activite_est_limitee_a_10_entrees() -> None:
    contexte = un_contexte_avec_douze_transitions()

    vues = contexte.lister_activite_recente().executer(DemandeActiviteRecente(), OUVRIER)

    assert len(vues) == LIMITE_PAR_DEFAUT


def test_sans_transition_l_activite_est_vide() -> None:
    contexte = Contexte()
    contexte.uow.etapes.ajouter(une_etape())

    assert contexte.lister_activite_recente().executer(DemandeActiviteRecente(), CHEF) == ()


@pytest.mark.parametrize("limite", [0, 51])
def test_une_limite_hors_des_bornes_est_refusee(limite: int) -> None:
    contexte = un_contexte_avec_de_l_activite()

    with pytest.raises(ValeurInvalideError):
        contexte.lister_activite_recente().executer(DemandeActiviteRecente(limite), CHEF)


def test_la_consultation_ne_valide_aucune_transaction() -> None:
    contexte = un_contexte_avec_de_l_activite()

    contexte.lister_activite_recente().executer(DemandeActiviteRecente(), CHEF)

    assert contexte.uow.validations == 0
