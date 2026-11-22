"""Objet valeur `Adresse` : l'endroit où se trouve un chantier."""

from dataclasses import dataclass

from app.shared.domain.erreurs import ValeurInvalideError
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
            ValeurInvalideError : la voie, le code postal ou la ville est vide, ou
                dépasse sa longueur maximale.
        """
        if not all(partie.strip() for partie in (self.voie, self.code_postal, self.ville)):
            raise ValeurInvalideError("La voie, le code postal et la ville sont obligatoires.")
        exiger_longueur_max(self.voie, LONGUEUR_VOIE_MAX, "La voie")
        exiger_longueur_max(self.code_postal, LONGUEUR_CODE_POSTAL_MAX, "Le code postal")
        exiger_longueur_max(self.ville, LONGUEUR_VILLE_MAX, "La ville")
