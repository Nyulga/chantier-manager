"""Contrôle des caractères d'un texte saisi, commun aux objets valeur des modules.

Un texte enregistré doit pouvoir être stocké, relu et affiché sans surprise. Trois
familles de caractères ne le permettent pas, et sont donc refusées :
- les caractères de contrôle (catégorie Unicode `Cc` : U+0000 à U+001F, U+007F à
  U+009F). Le caractère nul U+0000, en particulier, est refusé par PostgreSQL dans une
  colonne de texte (constat M4 du test d'intrusion, lot S6) : l'accepter aujourd'hui
  sous SQLite, ce serait garder des données que la future base ne pourra pas reprendre ;
- les demi-codets isolés (catégorie `Cs`), qu'aucun encodage UTF-8 ne sait écrire :
  ni SQLite ni PostgreSQL ne peuvent les enregistrer ;
- les caractères de mise en forme bidirectionnelle (U+202A à U+202E, U+2066 à U+2069).
  Ils inversent ou isolent le sens d'affichage du texte qui les suit : un texte peut
  alors s'afficher autrement qu'il n'est enregistré (usurpation d'affichage, attaque
  dite « Trojan Source »). Une saisie française n'en a jamais besoin, et un texte en
  arabe ou en hébreu s'affiche correctement sans eux, grâce à l'algorithme
  bidirectionnel d'Unicode. Les autres caractères de mise en forme restent permis :
  le liant sans chasse (U+200D) compose les emojis, et les marques de sens (U+200E,
  U+200F) ne peuvent pas réordonner un passage entier.

Le message d'erreur est fixe : il ne recopie jamais la saisie, qui pourrait contenir
une donnée personnelle ou le caractère fautif lui-même.
"""

import unicodedata

from app.shared.domain.erreurs import ValeurInvalideError

# Catégories Unicode refusées : les contrôles (`Cc`) et les demi-codets isolés (`Cs`).
CATEGORIES_INTERDITES = frozenset({"Cc", "Cs"})
# Enchâssements et forçages (U+202A à U+202E), puis isolats (U+2066 à U+2069). Ils sont
# construits par leurs numéros : écrits tels quels, ils seraient invisibles dans ce fichier.
CARACTERES_BIDIRECTIONNELS = frozenset(
    chr(code) for code in (*range(0x202A, 0x202F), *range(0x2066, 0x206A))
)
# Seuls contrôles admis dans un texte libre, sur plusieurs lignes. Le retour
# chariot est admis parce qu'une fin de ligne s'écrit `\r\n` sous Windows et dans les
# formulaires HTTP : le navigateur envoie `\n`, mais l'application mobile ou un autre
# client peut envoyer `\r\n`, et ce n'est pas une saisie hostile. La tabulation sert à
# aligner une énumération copiée d'un autre document.
CONTROLES_DE_MISE_EN_LIGNE = frozenset("\n\r\t")


def exiger_caracteres_sur_une_ligne(texte: str, libelle: str, champ: str) -> None:
    """Refuse un texte court, affiché sur une seule ligne, qui contient un caractère interdit.

    Tout caractère de contrôle est refusé, y compris le saut de ligne et la tabulation :
    un tel texte s'affiche sur une seule ligne, dans les listes et sur les cartes, où un
    saut de ligne casserait la mise en page.
    `libelle` et `champ` jouent le même rôle que pour `exiger_longueur_max`.

    Lève :
        ValeurInvalideError : le texte contient un caractère interdit.
    """
    _exiger_sans_caractere_interdit(texte, frozenset(), libelle, champ)


def exiger_caracteres_sur_plusieurs_lignes(texte: str, libelle: str, champ: str) -> None:
    """Refuse un texte libre, sur plusieurs lignes, qui contient un caractère interdit.

    Seuls le saut de ligne, le retour chariot et la tabulation y sont admis parmi les
    caractères de contrôle.

    Lève :
        ValeurInvalideError : le texte contient un caractère interdit.
    """
    _exiger_sans_caractere_interdit(texte, CONTROLES_DE_MISE_EN_LIGNE, libelle, champ)


def _exiger_sans_caractere_interdit(
    texte: str, admis: frozenset[str], libelle: str, champ: str
) -> None:
    """Lève `ValeurInvalideError` dès qu'un caractère interdit, et non admis ici, apparaît."""
    if any(_est_interdit(caractere) and caractere not in admis for caractere in texte):
        raise ValeurInvalideError(f"{libelle} contient un caractère non autorisé.", champ)


def _est_interdit(caractere: str) -> bool:
    """Dit si le caractère appartient à l'une des trois familles refusées."""
    return (
        unicodedata.category(caractere) in CATEGORIES_INTERDITES
        or caractere in CARACTERES_BIDIRECTIONNELS
    )
