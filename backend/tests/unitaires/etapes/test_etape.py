from uuid import UUID

import pytest

from app.etapes.domain.cycle import ActionEtape, StatutEtape
from app.etapes.domain.etape import Etape, HistoriqueEtape, ordre_suivant
from app.shared.domain.acteur import Acteur, Role
from app.shared.domain.erreurs import TransitionInterditeError, ValeurInvalideError
from tests.unitaires.etapes.fabriques import ID_CHANTIER, INSTANT, une_etape

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


def test_une_transition_interdite_ne_change_rien() -> None:
    etape = une_etape(StatutEtape.TERMINEE_A_VALIDER)

    with pytest.raises(TransitionInterditeError):
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
