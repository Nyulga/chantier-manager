"""Contrôle de la longueur maximale d'un texte, commun aux objets valeur des modules.

Les bornes elles-mêmes appartiennent au domaine de chaque module, sous forme de
constantes nommées : l'api et les colonnes de la base s'y réfèrent, pour qu'une
même limite ne soit écrite qu'une fois. Ce fichier ne fournit que la vérification.
"""

from app.shared.domain.erreurs import ValeurInvalideError


def exiger_longueur_max(texte: str, longueur_max: int, libelle: str, champ: str) -> None:
    """Refuse un texte plus long que `longueur_max` caractères.

    `libelle` désigne le texte dans le message, avec son article (« La voie »,
    « Le commentaire ») : le message est affiché tel quel, et ne recopie jamais la
    valeur saisie, qui pourrait contenir une donnée personnelle. `champ` nomme le
    champ de saisie fautif, pour que l'erreur s'affiche à son endroit.

    Lève :
        ValeurInvalideError : le texte dépasse la longueur maximale.
    """
    if len(texte) > longueur_max:
        raise ValeurInvalideError(
            f"{libelle} ne doit pas dépasser {longueur_max} caractères.", champ
        )
