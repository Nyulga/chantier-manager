"""Plafond du nombre de transitions par étape : 20, vérifié avant d'écrire quoi que ce soit.

La validation en est exemptée : elle mène à un statut final et ne peut donc pas
servir à boucler, alors qu'une étape pleine et non validable resterait à vie « À valider ».
"""

import pytest

from app.etapes.application.changer_statut_etape import ChangementStatut
from app.etapes.application.plafonds import LIMITE_TRANSITIONS_PAR_ETAPE
from app.etapes.domain.cycle import StatutEtape
from app.etapes.domain.etape import Etape, HistoriqueEtape
from app.shared.application.erreurs import PlafondAtteintError
from app.shared.domain.acteur import Acteur, Role
from app.shared.domain.erreurs import ConflitVersionError, TransitionInterditeError
from tests.application.etapes.contexte import Contexte
from tests.fabriques.etapes import INSTANT, id_etape, une_etape

CHEF = Acteur(Role.CHEF)
OUVRIER = Acteur(Role.OUVRIER)
ETAPE = id_etape(1)
AUTRE_ETAPE = id_etape(2)
# Plafond décidé par le propriétaire (ADR 0016).
PLAFOND_DECIDE = 20


def une_etape_avec_historique(statut: StatutEtape, transitions: int, ordre: int = 1) -> Etape:
    """Étape au statut donné, dont l'historique compte déjà `transitions` entrées.

    Les entrées sont toutes semblables : seul leur nombre compte pour le plafond.
    """
    etape = une_etape(statut, ordre=ordre)
    etape.historique = [
        HistoriqueEtape(Role.OUVRIER, StatutEtape.A_FAIRE, StatutEtape.EN_COURS, INSTANT, None)
        for _ in range(transitions)
    ]
    return etape


def un_contexte_avec(statut: StatutEtape, transitions: int) -> Contexte:
    contexte = Contexte()
    contexte.uow.etapes.ajouter(une_etape_avec_historique(statut, transitions))
    return contexte


def test_le_plafond_est_de_20_transitions_par_etape() -> None:
    assert LIMITE_TRANSITIONS_PAR_ETAPE == PLAFOND_DECIDE


def test_la_derniere_transition_sous_le_plafond_est_acceptee() -> None:
    contexte = un_contexte_avec(StatutEtape.TERMINEE_A_VALIDER, LIMITE_TRANSITIONS_PAR_ETAPE - 1)
    commande = ChangementStatut(ETAPE, "refuser", "Joints à reprendre.")

    vue = contexte.changer_statut().executer(commande, CHEF)

    etape = contexte.uow.etapes.obtenir(ETAPE)
    assert (vue.statut, len(etape.historique), contexte.uow.validations) == (
        "en_cours",
        LIMITE_TRANSITIONS_PAR_ETAPE,
        1,
    )


@pytest.mark.parametrize(
    ("statut", "commande", "acteur"),
    [
        (StatutEtape.A_FAIRE, ChangementStatut(ETAPE, "demarrer"), OUVRIER),
        (StatutEtape.EN_COURS, ChangementStatut(ETAPE, "signaler_terminee"), OUVRIER),
        (StatutEtape.TERMINEE_A_VALIDER, ChangementStatut(ETAPE, "refuser", "Non."), CHEF),
    ],
)
def test_au_plafond_toute_transition_sauf_la_validation_est_refusee_sans_rien_ecrire(
    statut: StatutEtape, commande: ChangementStatut, acteur: Acteur
) -> None:
    contexte = un_contexte_avec(statut, LIMITE_TRANSITIONS_PAR_ETAPE)

    with pytest.raises(PlafondAtteintError) as erreur:
        contexte.changer_statut().executer(commande, acteur)

    assert str(erreur.value) == "Cette étape a atteint sa limite de 20 changements de statut."
    etape = contexte.uow.etapes.obtenir(ETAPE)
    assert (etape.statut, etape.version, len(etape.historique), contexte.uow.validations) == (
        statut,
        1,
        LIMITE_TRANSITIONS_PAR_ETAPE,
        0,
    )


def test_au_plafond_le_chef_peut_encore_valider() -> None:
    contexte = un_contexte_avec(StatutEtape.TERMINEE_A_VALIDER, LIMITE_TRANSITIONS_PAR_ETAPE)

    vue = contexte.changer_statut().executer(ChangementStatut(ETAPE, "valider"), CHEF)

    etape = contexte.uow.etapes.obtenir(ETAPE)
    assert (vue.statut, len(etape.historique), contexte.uow.validations) == (
        "validee",
        LIMITE_TRANSITIONS_PAR_ETAPE + 1,
        1,
    )


def test_au_plafond_l_ouvrier_ne_peut_toujours_pas_valider() -> None:
    contexte = un_contexte_avec(StatutEtape.TERMINEE_A_VALIDER, LIMITE_TRANSITIONS_PAR_ETAPE)

    with pytest.raises(TransitionInterditeError):
        contexte.changer_statut().executer(ChangementStatut(ETAPE, "valider"), OUVRIER)

    etape = contexte.uow.etapes.obtenir(ETAPE)
    assert (etape.statut, len(etape.historique), contexte.uow.validations) == (
        StatutEtape.TERMINEE_A_VALIDER,
        LIMITE_TRANSITIONS_PAR_ETAPE,
        0,
    )


def test_au_plafond_une_version_perimee_reste_un_conflit() -> None:
    contexte = un_contexte_avec(StatutEtape.TERMINEE_A_VALIDER, LIMITE_TRANSITIONS_PAR_ETAPE)
    commande = ChangementStatut(ETAPE, "valider", version_attendue=2)

    with pytest.raises(ConflitVersionError):
        contexte.changer_statut().executer(commande, CHEF)

    assert contexte.uow.validations == 0


def test_le_plafond_d_une_autre_etape_ne_bloque_pas_celle_ci() -> None:
    contexte = un_contexte_avec(StatutEtape.TERMINEE_A_VALIDER, LIMITE_TRANSITIONS_PAR_ETAPE)
    contexte.uow.etapes.ajouter(une_etape_avec_historique(StatutEtape.A_FAIRE, 0, ordre=2))

    vue = contexte.changer_statut().executer(ChangementStatut(AUTRE_ETAPE, "demarrer"), OUVRIER)

    assert (vue.statut, contexte.uow.validations) == ("en_cours", 1)
