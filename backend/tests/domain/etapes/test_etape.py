"""Entité `Etape` : création, transitions, verrou de version, bornes et tri des signalements."""

from uuid import UUID

import pytest

from app.etapes.domain.cycle import ActionEtape, StatutEtape
from app.etapes.domain.etape import Etape, HistoriqueEtape, ordre_suivant, trier_par_signalement
from app.shared.domain.acteur import Acteur, Role
from app.shared.domain.erreurs import (
    AccesRefuseError,
    ConflitVersionError,
    TransitionInterditeError,
    ValeurInvalideError,
)
from tests.fabriques.etapes import (
    ID_CHANTIER,
    INSTANT,
    heures_apres,
    id_etape,
    une_etape,
    une_etape_signalee,
)

CHEF = Acteur(Role.CHEF)
OUVRIER = Acteur(Role.OUVRIER)
VERSION_APRES_UNE_TRANSITION = 2
ORDRE_APRES_LE_PLUS_GRAND = 6


def test_une_nouvelle_etape_est_a_faire_en_version_1_sans_historique() -> None:
    etape = Etape.creer(UUID(int=7), ID_CHANTIER, "Plomberie", ordre=3)

    assert etape == Etape(
        id=UUID(int=7),
        chantier_id=ID_CHANTIER,
        titre="Plomberie",
        ordre=3,
        statut=StatutEtape.A_FAIRE,
        version=1,
        historique=[],
    )


@pytest.mark.parametrize("titre", ["", "  ", "\t"])
def test_une_etape_sans_titre_est_refusee(titre: str) -> None:
    with pytest.raises(ValeurInvalideError):
        Etape.creer(UUID(int=7), ID_CHANTIER, titre, ordre=1)


def test_un_titre_de_200_caracteres_est_accepte() -> None:
    etape = Etape.creer(UUID(int=7), ID_CHANTIER, "t" * 200, ordre=1)

    assert etape.titre == "t" * 200


def test_un_titre_de_plus_de_200_caracteres_est_refuse() -> None:
    with pytest.raises(ValeurInvalideError):
        Etape.creer(UUID(int=7), ID_CHANTIER, "t" * 201, ordre=1)


def test_une_transition_change_le_statut_trace_l_historique_et_incremente_la_version() -> None:
    etape = une_etape()

    etape.appliquer(ActionEtape.DEMARRER, OUVRIER, INSTANT)

    assert etape.statut is StatutEtape.EN_COURS
    assert etape.version == VERSION_APRES_UNE_TRANSITION
    assert etape.historique == [
        HistoriqueEtape(
            role=Role.OUVRIER,
            ancien_statut=StatutEtape.A_FAIRE,
            nouveau_statut=StatutEtape.EN_COURS,
            date=INSTANT,
            commentaire=None,
        )
    ]


def test_un_refus_avec_commentaire_renvoie_en_cours_et_garde_le_commentaire() -> None:
    etape = une_etape(StatutEtape.TERMINEE_A_VALIDER)

    etape.appliquer(ActionEtape.REFUSER, CHEF, INSTANT, "Joints à reprendre.")

    assert etape.statut is StatutEtape.EN_COURS
    assert etape.historique[-1].commentaire == "Joints à reprendre."


@pytest.mark.parametrize("commentaire", [None, "", "   "])
def test_un_refus_sans_commentaire_est_refuse_et_ne_change_rien(commentaire: str | None) -> None:
    etape = une_etape(StatutEtape.TERMINEE_A_VALIDER)

    with pytest.raises(ValeurInvalideError):
        etape.appliquer(ActionEtape.REFUSER, CHEF, INSTANT, commentaire)

    assert (etape.statut, etape.version, etape.historique) == (
        StatutEtape.TERMINEE_A_VALIDER,
        1,
        [],
    )


@pytest.mark.parametrize(
    ("statut", "action", "acteur"),
    [
        (StatutEtape.A_FAIRE, ActionEtape.DEMARRER, OUVRIER),
        (StatutEtape.TERMINEE_A_VALIDER, ActionEtape.REFUSER, CHEF),
    ],
)
def test_un_commentaire_de_plus_de_1000_caracteres_est_refuse_et_ne_change_rien(
    statut: StatutEtape, action: ActionEtape, acteur: Acteur
) -> None:
    etape = une_etape(statut)

    with pytest.raises(ValeurInvalideError):
        etape.appliquer(action, acteur, INSTANT, "c" * 1001)

    assert (etape.statut, etape.version, etape.historique) == (statut, 1, [])


def test_un_commentaire_facultatif_de_1000_caracteres_est_garde() -> None:
    etape = une_etape()

    etape.appliquer(ActionEtape.DEMARRER, OUVRIER, INSTANT, "c" * 1000)

    assert etape.historique[-1].commentaire == "c" * 1000


@pytest.mark.parametrize("version_attendue", [None, 1])
def test_une_version_attendue_absente_ou_a_jour_est_acceptee(version_attendue: int | None) -> None:
    etape = une_etape()

    etape.verifier_version(version_attendue)

    assert etape.version == 1


@pytest.mark.parametrize("version_attendue", [0, 2])
def test_une_version_attendue_perimee_leve_un_conflit(version_attendue: int) -> None:
    etape = une_etape()

    with pytest.raises(ConflitVersionError):
        etape.verifier_version(version_attendue)


def test_une_transition_interdite_ne_change_rien() -> None:
    etape = une_etape(StatutEtape.TERMINEE_A_VALIDER)

    with pytest.raises(TransitionInterditeError):
        etape.appliquer(ActionEtape.DEMARRER, CHEF, INSTANT)

    assert (etape.statut, etape.version, etape.historique) == (
        StatutEtape.TERMINEE_A_VALIDER,
        1,
        [],
    )


def test_un_ouvrier_qui_tente_de_valider_recoit_un_refus_de_droit_sans_rien_changer() -> None:
    etape = une_etape(StatutEtape.TERMINEE_A_VALIDER)

    with pytest.raises(AccesRefuseError):
        etape.appliquer(ActionEtape.VALIDER, OUVRIER, INSTANT)

    assert (etape.statut, etape.version, etape.historique) == (
        StatutEtape.TERMINEE_A_VALIDER,
        1,
        [],
    )


def test_la_premiere_etape_d_un_chantier_a_l_ordre_1() -> None:
    assert ordre_suivant([]) == 1


def test_une_nouvelle_etape_se_place_apres_la_derniere() -> None:
    etapes = [une_etape(ordre=2), une_etape(ordre=5), une_etape(ordre=3)]

    assert ordre_suivant(etapes) == ORDRE_APRES_LE_PLUS_GRAND


def test_une_etape_jamais_signalee_n_a_pas_de_date_de_signalement() -> None:
    etape = une_etape()
    etape.appliquer(ActionEtape.DEMARRER, OUVRIER, INSTANT)

    assert etape.signalee_le() is None


def test_la_date_de_signalement_est_celle_de_la_transition_vers_a_valider() -> None:
    etape = une_etape_signalee(heures_apres(3))

    assert etape.signalee_le() == heures_apres(3)


def test_apres_un_refus_seul_le_dernier_signalement_compte() -> None:
    etape = une_etape_signalee(heures_apres(1))
    etape.appliquer(ActionEtape.REFUSER, CHEF, heures_apres(2), "Joints à reprendre.")
    etape.appliquer(ActionEtape.SIGNALER_TERMINEE, OUVRIER, heures_apres(5))
    etape.appliquer(ActionEtape.VALIDER, CHEF, heures_apres(6))

    assert etape.signalee_le() == heures_apres(5)


def test_les_etapes_sont_triees_de_la_plus_anciennement_signalee_a_la_plus_recente() -> None:
    recente = une_etape_signalee(heures_apres(9), ordre=1)
    ancienne = une_etape_signalee(heures_apres(2), ordre=2)
    moyenne = une_etape_signalee(heures_apres(5), ordre=3)

    triees = trier_par_signalement([recente, ancienne, moyenne])

    assert [etape.id for etape in triees] == [ancienne.id, moyenne.id, recente.id]


def test_a_date_egale_l_ordre_de_creation_departage_les_etapes() -> None:
    seconde = une_etape_signalee(heures_apres(4), ordre=2)
    premiere = une_etape_signalee(heures_apres(4), ordre=1)

    triees = trier_par_signalement([seconde, premiere])

    assert [etape.id for etape in triees] == [id_etape(1), id_etape(2)]


def test_une_etape_sans_signalement_connu_passe_en_tete_du_tri() -> None:
    signalee = une_etape_signalee(heures_apres(1), ordre=1)
    sans_trace = une_etape(StatutEtape.TERMINEE_A_VALIDER, ordre=2)
    autre_sans_trace = une_etape(StatutEtape.TERMINEE_A_VALIDER, ordre=3)

    triees = trier_par_signalement([signalee, autre_sans_trace, sans_trace])

    assert [etape.id for etape in triees] == [sans_trace.id, autre_sans_trace.id, signalee.id]


@pytest.mark.parametrize("titre", ["  ", "t" * 201])
def test_un_titre_refuse_designe_le_champ_titre(titre: str) -> None:
    with pytest.raises(ValeurInvalideError) as erreur:
        Etape.creer(UUID(int=7), ID_CHANTIER, titre, ordre=1)

    assert erreur.value.champ == "titre"


@pytest.mark.parametrize("commentaire", [None, "c" * 1001])
def test_un_commentaire_refuse_designe_le_champ_commentaire(commentaire: str | None) -> None:
    etape = une_etape(StatutEtape.TERMINEE_A_VALIDER)

    with pytest.raises(ValeurInvalideError) as erreur:
        etape.appliquer(ActionEtape.REFUSER, CHEF, INSTANT, commentaire)

    assert erreur.value.champ == "commentaire"
