"""Hiérarchie des erreurs métier communes."""

import pytest

from app.shared.domain.erreurs import (
    AccesRefuseError,
    ConflitVersionError,
    ErreurMetierError,
    NonTrouveError,
    TransitionInterditeError,
    ValeurInvalideError,
)


@pytest.mark.parametrize(
    "classe",
    [
        NonTrouveError,
        TransitionInterditeError,
        ValeurInvalideError,
        AccesRefuseError,
        ConflitVersionError,
    ],
)
def test_chaque_erreur_metier_herite_d_erreur_metier_et_garde_son_message(
    classe: type[ErreurMetierError],
) -> None:
    erreur = classe("Message en français.")

    assert isinstance(erreur, ErreurMetierError)
    assert str(erreur) == "Message en français."


def test_une_valeur_invalide_garde_le_champ_fautif() -> None:
    erreur = ValeurInvalideError("Le nom est obligatoire.", champ="nom")

    assert (str(erreur), erreur.champ) == ("Le nom est obligatoire.", "nom")


def test_une_valeur_invalide_sans_champ_est_globale() -> None:
    assert ValeurInvalideError("Valeur invalide.").champ is None
