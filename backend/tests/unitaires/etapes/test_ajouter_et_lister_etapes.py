from uuid import UUID

import pytest

from app.etapes.application.ajouter_etape import NouvelleEtape
from app.etapes.application.vues import EtapeVue
from app.etapes.domain.cycle import StatutEtape
from app.shared.domain.acteur import Acteur, Role
from app.shared.domain.erreurs import AccesRefuseError, NonTrouveError, ValeurInvalideError
from tests.unitaires.etapes.contexte import Contexte
from tests.unitaires.etapes.fabriques import ID_CHANTIER, id_etape, une_etape

CHEF = Acteur(Role.CHEF)
OUVRIER = Acteur(Role.OUVRIER)
AUTRE_CHANTIER = UUID(int=200)
INCONNU = UUID(int=999)


def test_un_chef_ajoute_une_etape_a_faire_en_fin_de_liste() -> None:
    contexte = Contexte()
    contexte.uow.etapes.ajouter(une_etape(ordre=4))

    vue = contexte.ajouter_etape().executer(NouvelleEtape(ID_CHANTIER, "Électricité"), CHEF)

    assert vue == EtapeVue(
        id=UUID(int=1),
        chantier_id=ID_CHANTIER,
        titre="Électricité",
        ordre=5,
        statut="a_faire",
        version=1,
        actions_permises=("demarrer",),
    )
    assert contexte.uow.etapes.obtenir(UUID(int=1)).titre == "Électricité"
    assert contexte.uow.validations == 1


def test_un_ouvrier_ne_peut_pas_ajouter_d_etape() -> None:
    contexte = Contexte()

    with pytest.raises(AccesRefuseError):
        contexte.ajouter_etape().executer(NouvelleEtape(ID_CHANTIER, "Électricité"), OUVRIER)

    assert (contexte.uow.etapes.lister_par_chantiers([ID_CHANTIER]), contexte.uow.validations) == (
        [],
        0,
    )


def test_ajouter_une_etape_a_un_chantier_inconnu_leve_non_trouve() -> None:
    contexte = Contexte()

    with pytest.raises(NonTrouveError):
        contexte.ajouter_etape().executer(NouvelleEtape(INCONNU, "Électricité"), CHEF)

    assert contexte.uow.validations == 0


def test_une_etape_sans_titre_n_est_pas_enregistree() -> None:
    contexte = Contexte()

    with pytest.raises(ValeurInvalideError):
        contexte.ajouter_etape().executer(NouvelleEtape(ID_CHANTIER, "  "), CHEF)

    assert (contexte.uow.etapes.lister_par_chantiers([ID_CHANTIER]), contexte.uow.validations) == (
        [],
        0,
    )


def test_la_liste_ne_contient_que_les_etapes_du_chantier_dans_l_ordre() -> None:
    contexte = Contexte()
    contexte.uow.etapes.ajouter(une_etape(ordre=2))
    contexte.uow.etapes.ajouter(une_etape(ordre=1, chantier_id=AUTRE_CHANTIER))
    contexte.uow.etapes.ajouter(une_etape(ordre=1))

    vues = contexte.lister_etapes().executer(ID_CHANTIER, CHEF)

    assert [vue.id for vue in vues] == [id_etape(1), id_etape(2)]


@pytest.mark.parametrize(
    ("acteur", "actions"),
    [(CHEF, ("valider", "refuser")), (OUVRIER, ())],
)
def test_la_liste_porte_les_actions_permises_au_role(
    acteur: Acteur, actions: tuple[str, ...]
) -> None:
    contexte = Contexte()
    contexte.uow.etapes.ajouter(une_etape(StatutEtape.TERMINEE_A_VALIDER))

    vues = contexte.lister_etapes().executer(ID_CHANTIER, acteur)

    assert [(vue.statut, vue.actions_permises) for vue in vues] == [("terminee_a_valider", actions)]


def test_un_chantier_sans_etape_donne_une_liste_vide() -> None:
    assert Contexte().lister_etapes().executer(ID_CHANTIER, OUVRIER) == ()


def test_lister_les_etapes_d_un_chantier_inconnu_leve_non_trouve() -> None:
    with pytest.raises(NonTrouveError):
        Contexte().lister_etapes().executer(INCONNU, CHEF)
