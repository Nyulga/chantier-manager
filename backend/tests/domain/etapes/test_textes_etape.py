"""Textes propres d'une étape : le titre tient sur une ligne, le commentaire sur plusieurs."""

from uuid import UUID

import pytest

from app.etapes.domain.cycle import ActionEtape, StatutEtape
from app.etapes.domain.etape import Etape
from app.shared.domain.acteur import Acteur, Role
from app.shared.domain.erreurs import ValeurInvalideError
from tests.fabriques.etapes import ID_CHANTIER, INSTANT, une_etape
from tests.fabriques.textes import (
    INTERDITS_PARTOUT,
    INTERDITS_SUR_UNE_LIGNE,
    SAUTS_ET_TABULATION,
    TEXTE_ACCEPTE,
)

OUVRIER = Acteur(Role.OUVRIER)


@pytest.mark.parametrize("caractere", INTERDITS_SUR_UNE_LIGNE)
def test_un_titre_avec_un_caractere_interdit_est_refuse(caractere: str) -> None:
    with pytest.raises(ValeurInvalideError) as erreur:
        Etape.creer(UUID(int=7), ID_CHANTIER, f"Gros{caractere}œuvre", ordre=1)

    assert (str(erreur.value), erreur.value.champ) == (
        "Le titre de l'étape contient un caractère non autorisé.",
        "titre",
    )


def test_un_titre_accentue_avec_emoji_compose_est_accepte() -> None:
    etape = Etape.creer(UUID(int=7), ID_CHANTIER, TEXTE_ACCEPTE, ordre=1)

    assert etape.titre == TEXTE_ACCEPTE


@pytest.mark.parametrize("caractere", INTERDITS_PARTOUT)
def test_un_commentaire_avec_un_caractere_interdit_est_refuse_sans_rien_changer(
    caractere: str,
) -> None:
    etape = une_etape()

    with pytest.raises(ValeurInvalideError) as erreur:
        etape.appliquer(ActionEtape.DEMARRER, OUVRIER, INSTANT, f"Reprendre{caractere}le joint")

    assert (str(erreur.value), erreur.value.champ) == (
        "Le commentaire contient un caractère non autorisé.",
        "commentaire",
    )
    assert (etape.statut, etape.version, etape.historique) == (StatutEtape.A_FAIRE, 1, [])


@pytest.mark.parametrize("caractere", SAUTS_ET_TABULATION)
def test_un_commentaire_sur_plusieurs_lignes_est_accepte(caractere: str) -> None:
    etape = une_etape()
    commentaire = f"Reprendre le joint.{caractere}Nettoyer ensuite."

    etape.appliquer(ActionEtape.DEMARRER, OUVRIER, INSTANT, commentaire)

    assert etape.historique[0].commentaire == commentaire
