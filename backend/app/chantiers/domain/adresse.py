"""Objet valeur `Adresse` : l'endroit où se trouve un chantier."""

from dataclasses import dataclass

from app.shared.domain.erreurs import ValeurInvalideError


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
        """Refuse une adresse dont une partie est vide ou ne contient que des espaces.

        Lève :
            ValeurInvalideError : la voie, le code postal ou la ville est vide.
        """
        if not all(partie.strip() for partie in (self.voie, self.code_postal, self.ville)):
            raise ValeurInvalideError("La voie, le code postal et la ville sont obligatoires.")
