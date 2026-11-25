"""Caractères de test pour la garde des textes propres, partagés par les modules.

Chaque liste couvre une famille de la garde (`app.shared.domain.caracteres`) : les
caractères de contrôle aux deux bouts de leurs plages, un demi-codet isolé, les
séparateurs de ligne et de paragraphe, l'usage privé, les caractères de mise en forme
(bidirectionnels compris) hors de la liste blanche, puis les textes sans aucun
caractère visible. Les caractères sont écrits par leur numéro : tels quels, la
plupart seraient invisibles dans ce fichier.
"""

import pytest

# Caractères refusés partout, y compris dans un texte sur plusieurs lignes. L'identifiant
# de chaque cas commence par la catégorie Unicode qu'il représente.
INTERDITS_PARTOUT = [
    pytest.param("\x00", id="Cc-nul"),
    pytest.param("\x07", id="Cc-sonnerie"),
    pytest.param("\x0b", id="Cc-tabulation-verticale"),
    pytest.param("\x1b", id="Cc-echappement"),
    pytest.param("\x1f", id="Cc-separateur-d-unite"),
    pytest.param("\x7f", id="Cc-suppression"),
    pytest.param("\x85", id="Cc-ligne-suivante-c1"),
    pytest.param("\x9f", id="Cc-fin-c1"),
    pytest.param("\ud800", id="Cs-demi-codet-isole"),
    pytest.param("\u2028", id="Zl-separateur-de-ligne"),
    pytest.param("\u2029", id="Zp-separateur-de-paragraphe"),
    pytest.param("\ue000", id="Co-usage-prive"),
    pytest.param("\U000f0000", id="Co-usage-prive-supplementaire"),
    pytest.param("\u202a", id="Cf-enchassement-gauche-droite"),
    pytest.param("\u202e", id="Cf-forcage-droite-gauche"),
    pytest.param("\u2066", id="Cf-isolat-gauche-droite"),
    pytest.param("\u2069", id="Cf-fin-d-isolat"),
    pytest.param("\u200b", id="Cf-espace-sans-chasse"),
    pytest.param("\u00ad", id="Cf-trait-d-union-conditionnel"),
    pytest.param("\u2060", id="Cf-gluon-de-mots"),
    pytest.param("\ufeff", id="Cf-indicateur-d-ordre-des-octets"),
    pytest.param("\U000e0001", id="Cf-etiquette-de-langue"),
]

# Sauts de ligne et tabulation : refusés sur une ligne, acceptés sur plusieurs lignes.
SAUTS_ET_TABULATION = [
    pytest.param("\n", id="saut-de-ligne"),
    pytest.param("\r", id="retour-chariot"),
    pytest.param("\r\n", id="fin-de-ligne-windows"),
    pytest.param("\t", id="tabulation"),
]

INTERDITS_SUR_UNE_LIGNE = INTERDITS_PARTOUT + SAUTS_ET_TABULATION

# Caractères de mise en forme (`Cf`) de la liste blanche, admis partout : ils servent à
# écrire le persan, les emojis composés, le sens d'un passage et les drapeaux régionaux.
MISE_EN_FORME_ADMISE = [
    pytest.param("\u200c", id="antiliant-sans-chasse"),
    pytest.param("\u200d", id="liant-sans-chasse"),
    pytest.param("\u200e", id="marque-gauche-droite"),
    pytest.param("\u200f", id="marque-droite-gauche"),
    pytest.param("\U000e0020", id="premiere-etiquette"),
    pytest.param("\U000e007f", id="fin-d-etiquette"),
]

# Drapeau de l'Écosse : un drapeau noir suivi des étiquettes « gbsct » et de la fin
# d'étiquette. C'est l'usage réel des caractères d'étiquette de la liste blanche.
DRAPEAU_ECOSSE = "\U0001f3f4\U000e0067\U000e0062\U000e0073\U000e0063\U000e0074\U000e007f"

# Point de code non attribué dans la base Unicode de Python (catégorie `Cn`) : il
# représente un emoji trop récent pour elle, qu'un téléphone peut pourtant envoyer.
NON_ATTRIBUE = "\u0378"

# Textes sans aucun caractère visible, refusés là où un texte est obligatoire : espaces
# (dont l'espace insécable et l'espace idéographique), liants, marques de sens, marques
# combinantes seules, étiquettes sans drapeau, ou un mélange de tout cela.
SANS_CARACTERE_VISIBLE = [
    pytest.param("", id="vide"),
    pytest.param("   ", id="espaces"),
    pytest.param("\u00a0\u3000", id="espaces-insecable-et-ideographique"),
    pytest.param("\u200d", id="liant-seul"),
    pytest.param("\u200c\u200e\u200f", id="antiliant-et-marques-de-sens"),
    pytest.param("\u0301", id="marque-combinante-seule"),
    pytest.param("\u0903\u20dd", id="marques-avec-chasse-et-englobante"),
    pytest.param("\U000e0067\U000e007f", id="etiquettes-sans-drapeau"),
    pytest.param(" \u200d\u0301 ", id="melange"),
]

# Texte légitime qui doit toujours passer : accents, ligature, apostrophe et tiret
# typographiques, et un emoji composé avec un liant sans chasse (U+200D), qui est un
# caractère de mise en forme comme les caractères bidirectionnels, mais inoffensif.
TEXTE_ACCEPTE = "Œ é\u2019\u2013\U0001f477\u200d\u2640\ufe0f"
