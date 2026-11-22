"""Cas d'usage `ListerEtapesAValider` : réservé au chef, trié et plafonné."""

from uuid import UUID

import pytest

from app.etapes.application.plafonds import LIMITE_A_VALIDER
from app.etapes.application.vues import EtapeAValiderVue
from app.etapes.domain.cycle import StatutEtape
from app.shared.domain.acteur import Acteur, Role
from app.shared.domain.erreurs import AccesRefuseError
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
# Une étape signalée passe par deux transitions : sa version vaut donc 3.
VERSION_APRES_SIGNALEMENT = 3


def un_contexte_avec_des_etapes_de_chaque_statut() -> Contexte:
    contexte = Contexte()
    contexte.uow.etapes.ajouter(une_etape_signalee(heures_apres(8), ordre=1))
    contexte.uow.etapes.ajouter(une_etape(StatutEtape.A_FAIRE, ordre=2))
    contexte.uow.etapes.ajouter(une_etape(StatutEtape.EN_COURS, ordre=3))
    contexte.uow.etapes.ajouter(une_etape(StatutEtape.VALIDEE, ordre=4))
    contexte.uow.etapes.ajouter(
        une_etape_signalee(heures_apres(2), ordre=1, chantier_id=AUTRE_CHANTIER)
    )
    return contexte


def un_contexte_avec_une_etape_de_trop_a_valider() -> Contexte:
    """Une étape à valider de plus que le plafond, signalées dans l'ordre inverse de leur création.

    L'étape d'ordre `n` est signalée `n` heures avant `INSTANT` : l'étape d'ordre 1
    est donc la plus récemment signalée. C'est elle qui doit rester hors de la
    liste, bien qu'elle ait le plus petit identifiant.
    """
    contexte = Contexte()
    for ordre in range(1, LIMITE_A_VALIDER + 2):
        contexte.uow.etapes.ajouter(une_etape_signalee(heures_apres(-ordre), ordre=ordre))
    return contexte


def test_le_chef_voit_les_etapes_a_valider_de_tous_les_chantiers_les_plus_anciennes_d_abord() -> (
    None
):
    contexte = un_contexte_avec_des_etapes_de_chaque_statut()

    vues = contexte.lister_etapes_a_valider().executer(CHEF)

    assert [(vue.id, vue.signalee_le) for vue in vues] == [
        (id_etape(1, AUTRE_CHANTIER), heures_apres(2)),
        (id_etape(1), heures_apres(8)),
    ]


def test_chaque_etape_a_valider_porte_ses_actions_et_sa_version() -> None:
    contexte = Contexte()
    contexte.uow.etapes.ajouter(une_etape_signalee(heures_apres(1)))

    vues = contexte.lister_etapes_a_valider().executer(CHEF)

    assert vues == (
        EtapeAValiderVue(
            id=id_etape(1),
            chantier_id=ID_CHANTIER,
            titre="Gros œuvre",
            version=VERSION_APRES_SIGNALEMENT,
            actions_permises=("valider", "refuser"),
            signalee_le=heures_apres(1),
        ),
    )


def test_sans_etape_a_valider_la_liste_est_vide() -> None:
    contexte = Contexte()
    contexte.uow.etapes.ajouter(une_etape(StatutEtape.EN_COURS))

    assert contexte.lister_etapes_a_valider().executer(CHEF) == ()


def test_un_ouvrier_ne_peut_pas_consulter_les_etapes_a_valider() -> None:
    contexte = un_contexte_avec_des_etapes_de_chaque_statut()

    with pytest.raises(AccesRefuseError):
        contexte.lister_etapes_a_valider().executer(OUVRIER)


def test_la_consultation_ne_valide_aucune_transaction() -> None:
    contexte = un_contexte_avec_des_etapes_de_chaque_statut()

    contexte.lister_etapes_a_valider().executer(CHEF)

    assert contexte.uow.validations == 0


def test_la_liste_a_valider_est_plafonnee_aux_etapes_signalees_depuis_le_plus_longtemps() -> None:
    contexte = un_contexte_avec_une_etape_de_trop_a_valider()

    vues = contexte.lister_etapes_a_valider().executer(CHEF)

    assert [vue.id for vue in vues] == [
        id_etape(ordre) for ordre in range(LIMITE_A_VALIDER + 1, 1, -1)
    ]
