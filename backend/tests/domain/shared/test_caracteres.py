"""Garde des textes propres : caractères refusés sur une ligne et sur plusieurs lignes."""

from collections.abc import Callable

import pytest

from app.shared.domain.caracteres import (
    exiger_caracteres_sur_plusieurs_lignes,
    exiger_caracteres_sur_une_ligne,
)
from app.shared.domain.erreurs import ValeurInvalideError
from tests.fabriques.textes import (
    INTERDITS_PARTOUT,
    INTERDITS_SUR_UNE_LIGNE,
    SAUTS_ET_TABULATION,
    TEXTE_ACCEPTE,
)

MESSAGE_ATTENDU = "La voie contient un caractère non autorisé."


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


@pytest.mark.parametrize(
    "garde", [exiger_caracteres_sur_une_ligne, exiger_caracteres_sur_plusieurs_lignes]
)
def test_un_texte_accentue_avec_emoji_compose_est_accepte_par_les_deux_gardes(
    garde: Callable[[str, str, str], None],
) -> None:
    garde(TEXTE_ACCEPTE, "La voie", "adresse.voie")
