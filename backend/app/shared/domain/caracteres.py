"""Contrôle des caractères d'un texte saisi, commun aux objets valeur des modules.

Un texte enregistré doit pouvoir être stocké, relu et affiché sans surprise. Cinq
familles de caractères ne le permettent pas, et sont donc refusées :
- les caractères de contrôle (catégorie Unicode `Cc` : U+0000 à U+001F, U+007F à
  U+009F). Le caractère nul U+0000, en particulier, est refusé par PostgreSQL dans une
  colonne de texte (constat M4 du test d'intrusion, lot S6) : l'accepter aujourd'hui
  sous SQLite, ce serait garder des données que la future base ne pourra pas reprendre ;
- les demi-codets isolés (catégorie `Cs`), qu'aucun encodage UTF-8 ne sait écrire :
  ni SQLite ni PostgreSQL ne peuvent les enregistrer ;
- les séparateurs de ligne et de paragraphe (U+2028 et U+2029, catégories `Zl` et
  `Zp`). Ce sont des sauts de ligne déguisés : ils casseraient l'affichage d'un texte
  sur une ligne, et le saut de ligne ordinaire (`\n`) suffit à un texte sur plusieurs
  lignes (issue #49) ;
- les caractères d'usage privé (catégorie `Co`), dont le dessin dépend de la police
  installée : le même texte s'afficherait différemment d'un appareil à l'autre ;
- les caractères de mise en forme (catégorie `Cf`), sauf une courte liste blanche.
  Ils sont invisibles, et certains changent l'affichage du texte qui les suit : les
  caractères bidirectionnels (U+202A à U+202E, U+2066 à U+2069) inversent ou isolent
  le sens d'affichage, si bien qu'un texte peut s'afficher autrement qu'il n'est
  enregistré (usurpation d'affichage, attaque dite « Trojan Source ») ; d'autres,
  comme l'espace sans chasse (U+200B), rendent différents deux textes identiques à
  l'œil. Une saisie française n'en a jamais besoin, et un texte en arabe ou en hébreu
  s'affiche correctement sans eux, grâce à l'algorithme bidirectionnel d'Unicode.

Les caractères non attribués (catégorie `Cn`) restent acceptés : la base Unicode de
Python a toujours une version de retard sur les téléphones, et les emojis les plus
récents y figurent comme non attribués. Les refuser bloquerait des saisies légitimes.

Enfin, un texte obligatoire doit contenir au moins un caractère visible : un nom fait
seulement d'espaces ou de liants s'afficherait comme une case vide (voir
`exiger_texte_visible`).

Les messages d'erreur sont fixes : ils ne recopient jamais la saisie, qui pourrait
contenir une donnée personnelle ou le caractère fautif lui-même.
"""

import unicodedata

from app.shared.domain.erreurs import ValeurInvalideError

# Catégories Unicode refusées : contrôles, demi-codets isolés, séparateurs de ligne et
# de paragraphe, usage privé et mise en forme (sauf la liste blanche ci-dessous).
CATEGORIES_INTERDITES = frozenset({"Cc", "Cs", "Zl", "Zp", "Co", "Cf"})
# Caractères de mise en forme qui servent vraiment, admis malgré leur catégorie `Cf` :
# l'antiliant sans chasse (U+200C), indispensable au persan ; le liant sans chasse
# (U+200D), qui compose les emojis (une famille, un métier) ; les marques de sens
# (U+200E, U+200F), qui orientent un signe isolé sans pouvoir réordonner un passage
# entier ; et les caractères d'étiquette (U+E0020 à U+E007F), qui forment les drapeaux
# régionaux, comme celui de l'Écosse. Ils sont construits par leurs numéros : écrits
# tels quels, ils seraient invisibles dans ce fichier.
MISE_EN_FORME_ADMISE = frozenset(
    chr(code) for code in (*range(0x200C, 0x2010), *range(0xE0020, 0xE0080))
)
# Seuls contrôles admis dans un texte libre, sur plusieurs lignes. Le retour
# chariot est admis parce qu'une fin de ligne s'écrit `\r\n` sous Windows et dans les
# formulaires HTTP : le navigateur envoie `\n`, mais l'application mobile ou un autre
# client peut envoyer `\r\n`, et ce n'est pas une saisie hostile. La tabulation sert à
# aligner une énumération copiée d'un autre document.
CONTROLES_DE_MISE_EN_LIGNE = frozenset("\n\r\t")
# Catégories dont aucun caractère ne se voit à lui seul : les espaces et séparateurs
# (`Z…`), les contrôles et la mise en forme (`Cc`, `Cf`), et les marques combinantes
# (`M…`), qui ne font que modifier le caractère qui les précède. Les catégories `Cs` et
# `Co` n'y figurent pas, car elles sont déjà refusées, avec un message plus juste ; ni
# `Cn`, pour qu'un emoji trop récent pour Python compte comme un caractère visible.
CATEGORIES_INVISIBLES = frozenset({"Zs", "Zl", "Zp", "Cc", "Cf", "Mn", "Mc", "Me"})


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


def exiger_texte_visible(texte: str, libelle: str, champ: str) -> None:
    """Refuse un texte obligatoire qui ne contient aucun caractère visible.

    Un tel texte, vide ou fait seulement d'espaces, de liants, de marques de sens ou de
    marques combinantes, s'afficherait comme une case vide : il compte donc comme
    absent, avec le même message qu'un champ laissé vide. `libelle` et `champ` jouent
    le même rôle que pour `exiger_longueur_max`.

    Lève :
        ValeurInvalideError : le texte ne contient aucun caractère visible.
    """
    if not contient_un_caractere_visible(texte):
        raise ValeurInvalideError(f"{libelle} est obligatoire.", champ)


def contient_un_caractere_visible(texte: str) -> bool:
    """Dit si le texte contient au moins un caractère qui se voit à lui seul.

    Un caractère est visible s'il n'appartient à aucune catégorie de
    `CATEGORIES_INVISIBLES` : ni espace ou séparateur, ni contrôle ou mise en forme,
    ni marque combinante. Le parcours s'arrête au premier caractère visible, qui est
    en pratique le premier du texte.
    """
    return any(unicodedata.category(caractere) not in CATEGORIES_INVISIBLES for caractere in texte)


def _exiger_sans_caractere_interdit(
    texte: str, admis: frozenset[str], libelle: str, champ: str
) -> None:
    """Lève `ValeurInvalideError` dès qu'un caractère interdit, et non admis ici, apparaît."""
    if any(_est_interdit(caractere) and caractere not in admis for caractere in texte):
        raise ValeurInvalideError(f"{libelle} contient un caractère non autorisé.", champ)


def _est_interdit(caractere: str) -> bool:
    """Dit si le caractère appartient à une famille refusée, hors de la liste blanche."""
    return (
        unicodedata.category(caractere) in CATEGORIES_INTERDITES
        and caractere not in MISE_EN_FORME_ADMISE
    )
