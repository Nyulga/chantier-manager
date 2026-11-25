"""Objet valeur `Adresse` : l'endroit où se trouve un chantier."""

from dataclasses import dataclass

from app.shared.domain.caracteres import exiger_caracteres_sur_une_ligne, exiger_texte_visible
from app.shared.domain.longueur import exiger_longueur_max

# Bornes de saisie de l'adresse. Elles sont larges pour une adresse française réelle,
# et empêchent qu'un texte démesuré soit enregistré puis affiché partout. L'api et
# les colonnes de la base s'y réfèrent : une seule source pour chaque limite.
LONGUEUR_VOIE_MAX = 300
LONGUEUR_CODE_POSTAL_MAX = 10
LONGUEUR_VILLE_MAX = 100


@dataclass(frozen=True, slots=True)
class Adresse:
    """Adresse postale d'un chantier, dont chaque partie est obligatoire.

    Une adresse incomplète ne permet pas de se rendre sur le chantier : elle ne
    doit donc pas pouvoir exister. Le domaine ne retire pas les espaces superflus ;
    c'est à l'api de nettoyer la saisie avant de la transmettre.
    """

    voie: str
    code_postal: str
    ville: str

    def __post_init__(self) -> None:
        """Refuse une adresse dont une partie est vide, ou plus longue que sa borne.

        Lève :
            ValeurInvalideError : la voie, le code postal ou la ville est vide (sans aucun
                caractère visible), dépasse
                sa longueur maximale ou contient un caractère interdit (un saut de
                ligne, par exemple). L'erreur désigne la partie fautive.
        """
        _exiger_partie(self.voie, "voie", "La voie", LONGUEUR_VOIE_MAX)
        _exiger_partie(self.code_postal, "code_postal", "Le code postal", LONGUEUR_CODE_POSTAL_MAX)
        _exiger_partie(self.ville, "ville", "La ville", LONGUEUR_VILLE_MAX)


def _exiger_partie(texte: str, partie: str, libelle: str, longueur_max: int) -> None:
    """Exige une partie d'adresse non vide, assez courte et propre, en désignant son champ.

    Le champ s'écrit `adresse.<partie>` : c'est le nom que l'api donne à l'adresse
    d'un chantier, la seule adresse que le domaine manipule.
    """
    champ = f"adresse.{partie}"
    exiger_texte_visible(texte, libelle, champ)
    exiger_longueur_max(texte, longueur_max, libelle, champ)
    # La longueur est contrôlée d'abord : le parcours des caractères reste ainsi borné.
    exiger_caracteres_sur_une_ligne(texte, libelle, champ)
