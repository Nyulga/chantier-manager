"""Textes propres du chantier : chaque champ texte refuse les caractères interdits.

Tous les champs texte d'un chantier tiennent sur une ligne : nom, client et les trois
parties de l'adresse. Tous sont obligatoires : un texte sans aucun caractère visible y
compte comme absent. Un texte refusé l'est en désignant son champ.
"""

from collections.abc import Callable

import pytest

from app.chantiers.domain.adresse import Adresse
from app.shared.domain.erreurs import ValeurInvalideError
from tests.fabriques.chantiers import une_fiche
from tests.fabriques.textes import (
    INTERDITS_SUR_UNE_LIGNE,
    SANS_CARACTERE_VISIBLE,
    TEXTE_ACCEPTE,
)

# Pour chaque champ, tel que l'api le nomme, la construction qui place le texte à tester
# dans ce champ, les autres restant valides.
CONSTRUCTIONS: dict[str, Callable[[str], object]] = {
    "nom": lambda texte: une_fiche(nom=texte),
    "client": lambda texte: une_fiche(client=texte),
    "adresse.voie": lambda texte: Adresse(voie=texte, code_postal="69001", ville="Lyon"),
    "adresse.code_postal": lambda texte: Adresse(voie="1 rue", code_postal=texte, ville="Lyon"),
    "adresse.ville": lambda texte: Adresse(voie="1 rue", code_postal="69001", ville=texte),
}


@pytest.mark.parametrize("caractere", INTERDITS_SUR_UNE_LIGNE)
@pytest.mark.parametrize("champ", CONSTRUCTIONS)
def test_un_caractere_interdit_est_refuse_en_designant_son_champ(
    champ: str, caractere: str
) -> None:
    with pytest.raises(ValeurInvalideError) as erreur:
        CONSTRUCTIONS[champ](f"A{caractere}B")

    assert erreur.value.champ == champ
    assert "contient un caractère non autorisé" in str(erreur.value)


@pytest.mark.parametrize("champ", CONSTRUCTIONS)
def test_un_texte_accentue_avec_emoji_compose_est_accepte(champ: str) -> None:
    CONSTRUCTIONS[champ](TEXTE_ACCEPTE)


# Message d'absence de chaque champ : il nomme le champ, jamais la saisie.
MESSAGES_D_ABSENCE = {
    "nom": "Le nom du chantier est obligatoire.",
    "client": "Le client du chantier est obligatoire.",
    "adresse.voie": "La voie est obligatoire.",
    "adresse.code_postal": "Le code postal est obligatoire.",
    "adresse.ville": "La ville est obligatoire.",
}


@pytest.mark.parametrize("texte", SANS_CARACTERE_VISIBLE)
@pytest.mark.parametrize("champ", CONSTRUCTIONS)
def test_un_texte_sans_caractere_visible_est_refuse_comme_absent(champ: str, texte: str) -> None:
    with pytest.raises(ValeurInvalideError) as erreur:
        CONSTRUCTIONS[champ](texte)

    assert (str(erreur.value), erreur.value.champ) == (MESSAGES_D_ABSENCE[champ], champ)
