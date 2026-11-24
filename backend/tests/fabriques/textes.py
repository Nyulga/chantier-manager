"""Caractères de test pour la garde des textes propres, partagés par les modules.

Chaque liste couvre une famille de la garde (`app.shared.domain.caracteres`) : les
caractères de contrôle aux deux bouts de leurs plages, un demi-codet isolé et les
caractères de mise en forme bidirectionnelle.
"""

import pytest

# Caractères refusés partout, y compris dans un texte sur plusieurs lignes.
INTERDITS_PARTOUT = [
    pytest.param("\x00", id="nul"),
    pytest.param("\x07", id="sonnerie"),
    pytest.param("\x0b", id="tabulation-verticale"),
    pytest.param("\x1b", id="echappement"),
    pytest.param("\x1f", id="separateur-d-unite"),
    pytest.param("\x7f", id="suppression"),
    pytest.param("\x85", id="ligne-suivante-c1"),
    pytest.param("\x9f", id="fin-c1"),
    pytest.param("\ud800", id="demi-codet-isole"),
    pytest.param("\u202a", id="enchassement-gauche-droite"),
    pytest.param("\u202e", id="forcage-droite-gauche"),
    pytest.param("\u2066", id="isolat-gauche-droite"),
    pytest.param("\u2069", id="fin-d-isolat"),
]

# Sauts de ligne et tabulation : refusés sur une ligne, acceptés sur plusieurs lignes.
SAUTS_ET_TABULATION = [
    pytest.param("\n", id="saut-de-ligne"),
    pytest.param("\r", id="retour-chariot"),
    pytest.param("\r\n", id="fin-de-ligne-windows"),
    pytest.param("\t", id="tabulation"),
]

INTERDITS_SUR_UNE_LIGNE = INTERDITS_PARTOUT + SAUTS_ET_TABULATION

# Texte légitime qui doit toujours passer : accents, ligature, apostrophe et tiret
# typographiques, et un emoji composé avec un liant sans chasse (U+200D), qui est un
# caractère de mise en forme comme les caractères bidirectionnels, mais inoffensif.
TEXTE_ACCEPTE = "Œ é\u2019\u2013\U0001f477\u200d\u2640\ufe0f"
