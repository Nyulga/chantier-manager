"""Schémas JSON des routes des chantiers : ce que l'API reçoit et ce qu'elle renvoie."""

from datetime import date
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

# Les espaces autour de la saisie sont retirés ici : le domaine ne le fait pas (`Adresse`).
CONFIG_ENTREE = ConfigDict(extra="forbid", frozen=True, str_strip_whitespace=True)
CONFIG_SORTIE = ConfigDict(extra="forbid", frozen=True)

LONGUEUR_NOM_MAX = 200
LONGUEUR_VOIE_MAX = 300
LONGUEUR_CODE_POSTAL_MAX = 10
LONGUEUR_VILLE_MAX = 100


class AdresseRequete(BaseModel):
    """Adresse postale saisie pour un chantier."""

    model_config = CONFIG_ENTREE

    voie: str = Field(max_length=LONGUEUR_VOIE_MAX)
    code_postal: str = Field(max_length=LONGUEUR_CODE_POSTAL_MAX)
    ville: str = Field(max_length=LONGUEUR_VILLE_MAX)


class CreerChantierRequete(BaseModel):
    """Corps de la création d'un chantier ; le budget est en euros, au centime près."""

    model_config = CONFIG_ENTREE

    nom: str = Field(max_length=LONGUEUR_NOM_MAX)
    adresse: AdresseRequete
    client: str = Field(max_length=LONGUEUR_NOM_MAX)
    date_debut: date
    echeance: date
    budget: Decimal


class AdresseReponse(BaseModel):
    """Adresse postale d'un chantier."""

    model_config = CONFIG_SORTIE

    voie: str
    code_postal: str
    ville: str


class ChantierReponse(BaseModel):
    """Chantier tel que le voit l'acteur.

    `budget` est une chaîne décimale en euros (`"125000.50"`), ou `null` pour un
    ouvrier. `avancement` est un pourcentage entier de 0 à 100.
    """

    model_config = CONFIG_SORTIE

    id: UUID
    nom: str
    adresse: AdresseReponse
    client: str
    date_debut: date
    echeance: date
    budget: Decimal | None
    avancement: int
    peut_ajouter_etape: bool
