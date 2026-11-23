"""Schémas JSON des routes des chantiers : ce que l'API reçoit et ce qu'elle renvoie."""

from datetime import date
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field

from app.chantiers.application.valeurs_publiques import (
    LONGUEUR_CLIENT_MAX,
    LONGUEUR_CODE_POSTAL_MAX,
    LONGUEUR_NOM_MAX,
    LONGUEUR_VILLE_MAX,
    LONGUEUR_VOIE_MAX,
)
from app.shared.api.schemas import CONFIG_ENTREE, CONFIG_SORTIE


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
    client: str = Field(max_length=LONGUEUR_CLIENT_MAX)
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
    ouvrier. `avancement` est un pourcentage entier de 0 à 100. Lui comme les
    compteurs d'étapes sont calculés à chaque lecture, jamais stockés.
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
    etapes_validees: int = Field(description="Nombre d'étapes validées du chantier.")
    etapes_total: int = Field(description="Nombre total d'étapes du chantier.")
    etapes_a_valider: int = Field(
        description="Nombre d'étapes signalées terminées, qui attendent la décision d'un chef."
    )
    jours_restants: int = Field(
        ge=0,
        description=(
            "Nombre de jours entiers, toujours positif ou nul. Si `en_retard` est faux, "
            "c'est le temps qui reste avant l'échéance (0 le jour même). Si `en_retard` "
            "est vrai, c'est le nombre de jours de retard depuis l'échéance, au moins 1."
        ),
    )
    en_retard: bool = Field(
        description="Vrai quand l'échéance est dépassée d'au moins un jour entier."
    )
    peut_ajouter_etape: bool
