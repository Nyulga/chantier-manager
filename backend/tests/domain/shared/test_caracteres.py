"""Garde des textes propres : caractères refusés, liste blanche et texte sans caractère visible."""

import unicodedata
from collections.abc import Callable

import pytest

from app.shared.domain.caracteres import (
    contient_un_caractere_visible,
    exiger_caracteres_sur_plusieurs_lignes,
    exiger_caracteres_sur_une_ligne,
    exiger_texte_visible,
)
from app.shared.domain.erreurs import ValeurInvalideError
from tests.fabriques.textes import (
    DRAPEAU_ECOSSE,
    INTERDITS_PARTOUT,
    INTERDITS_SUR_UNE_LIGNE,
    MISE_EN_FORME_ADMISE,
    NON_ATTRIBUE,
    SANS_CARACTERE_VISIBLE,
    SAUTS_ET_TABULATION,
    TEXTE_ACCEPTE,
)

MESSAGE_ATTENDU = "La voie contient un caractère non autorisé."
GARDES = [exiger_caracteres_sur_une_ligne, exiger_caracteres_sur_plusieurs_lignes]


@pytest.mark.parametrize("caractere", INTERDITS_SUR_UNE_LIGNE)
def test_un_texte_sur_une_ligne_refuse_les_controles_sauts_et_tabulations(caractere: str) -> None:
    with pytest.raises(ValeurInvalideError) as erreur:
        exiger_caracteres_sur_une_ligne(f"SAISIE{caractere}FIN", "La voie", "adresse.voie")

    assert (str(erreur.value), erreur.value.champ) == (MESSAGE_ATTENDU, "adresse.voie")


@pytest.mark.parametrize("caractere", INTERDITS_PARTOUT)
def test_un_texte_sur_plusieurs_lignes_refuse_les_autres_controles(caractere: str) -> None:
    with pytest.raises(ValeurInvalideError) as erreur:
        exiger_caracteres_sur_plusieurs_lignes(f"SAISIE{caractere}FIN", "La voie", "adresse.voie")

    assert (str(erreur.value), erreur.value.champ) == (MESSAGE_ATTENDU, "adresse.voie")


@pytest.mark.parametrize("caractere", SAUTS_ET_TABULATION)
def test_un_texte_sur_plusieurs_lignes_accepte_sauts_de_ligne_et_tabulation(
    caractere: str,
) -> None:
    exiger_caracteres_sur_plusieurs_lignes(f"Ligne{caractere}suivante", "La voie", "adresse.voie")


@pytest.mark.parametrize("garde", GARDES)
def test_un_texte_accentue_avec_emoji_compose_est_accepte_par_les_deux_gardes(
    garde: Callable[[str, str, str], None],
) -> None:
    garde(TEXTE_ACCEPTE, "La voie", "adresse.voie")


@pytest.mark.parametrize("caractere", MISE_EN_FORME_ADMISE)
@pytest.mark.parametrize("garde", GARDES)
def test_la_mise_en_forme_de_la_liste_blanche_est_acceptee_par_les_deux_gardes(
    garde: Callable[[str, str, str], None], caractere: str
) -> None:
    garde(f"SAISIE{caractere}FIN", "La voie", "adresse.voie")


@pytest.mark.parametrize("garde", GARDES)
def test_un_drapeau_regional_compose_d_etiquettes_est_accepte(
    garde: Callable[[str, str, str], None],
) -> None:
    garde(f"Rue d'{DRAPEAU_ECOSSE} Édimbourg", "La voie", "adresse.voie")


@pytest.mark.parametrize("garde", GARDES)
def test_un_caractere_non_attribue_reste_accepte_comme_un_emoji_trop_recent(
    garde: Callable[[str, str, str], None],
) -> None:
    categorie = unicodedata.category(NON_ATTRIBUE)

    garde(f"SAISIE{NON_ATTRIBUE}FIN", "La voie", "adresse.voie")

    assert categorie == "Cn"


@pytest.mark.parametrize("texte", SANS_CARACTERE_VISIBLE)
def test_un_texte_sans_caractere_visible_est_refuse_comme_absent(texte: str) -> None:
    with pytest.raises(ValeurInvalideError) as erreur:
        exiger_texte_visible(texte, "La voie", "adresse.voie")

    assert (str(erreur.value), erreur.value.champ) == ("La voie est obligatoire.", "adresse.voie")


@pytest.mark.parametrize(
    "texte",
    [
        pytest.param("A", id="lettre"),
        pytest.param("7", id="chiffre"),
        pytest.param(".", id="ponctuation"),
        pytest.param("\U0001f477", id="emoji"),
        pytest.param(NON_ATTRIBUE, id="non-attribue"),
        pytest.param(DRAPEAU_ECOSSE, id="drapeau-regional"),
        pytest.param(TEXTE_ACCEPTE, id="texte-accentue"),
    ],
)
def test_un_seul_caractere_visible_suffit_a_rendre_le_texte_present(texte: str) -> None:
    exiger_texte_visible(f"  {texte}  ", "La voie", "adresse.voie")

    assert contient_un_caractere_visible(texte)


@pytest.mark.parametrize("texte", SANS_CARACTERE_VISIBLE)
def test_un_texte_sans_caractere_visible_est_reconnu_comme_tel(texte: str) -> None:
    assert not contient_un_caractere_visible(texte)
