"""Schémas JSON des routes des chantiers : ce que l'API reçoit et ce qu'elle renvoie."""

from datetime import date
from decimal import Decimal
from typing import Annotated, Any
from uuid import UUID

from pydantic import BaseModel, BeforeValidator, Field, WithJsonSchema
from pydantic_core import PydanticCustomError

from app.chantiers.application.valeurs_publiques import (
    CHIFFRES_MONTANT_MAX,
    DECIMALES_MONTANT,
    LONGUEUR_CLIENT_MAX,
    LONGUEUR_CODE_POSTAL_MAX,
    LONGUEUR_NOM_MAX,
    LONGUEUR_VILLE_MAX,
    LONGUEUR_VOIE_MAX,
)
from app.shared.api.champ_piege import ChampPiege
from app.shared.api.schemas import CONFIG_ENTREE, CONFIG_SORTIE


class AdresseRequete(BaseModel):
    """Adresse postale saisie pour un chantier."""

    model_config = CONFIG_ENTREE

    voie: str = Field(max_length=LONGUEUR_VOIE_MAX)
    code_postal: str = Field(max_length=LONGUEUR_CODE_POSTAL_MAX)
    ville: str = Field(max_length=LONGUEUR_VILLE_MAX)


def _exiger_un_texte(valeur: Any) -> Any:
    """Refuse un nombre JSON : un flottant perd en précision avant même d'être lu.

    L'erreur reprend le type `decimal_type`, dont le message en français est déjà prévu
    (`erreurs_validation.py`) et ne recopie pas la valeur.
    """
    if not isinstance(valeur, str):
        raise PydanticCustomError("decimal_type", "Le montant doit être un texte décimal.")
    return valeur


# Montant reçu comme texte décimal (`"1234.50"`) : les montants sont des `Decimal`, jamais des
# flottants (intent.md). Le schéma OpenAPI l'annonce comme une chaîne, pour le client généré.
MontantTexte = Annotated[
    Decimal,
    BeforeValidator(_exiger_un_texte),
    WithJsonSchema({"type": "string", "examples": ["1234.50"]}),
]


class CreerChantierRequete(ChampPiege):
    """Corps de la création d'un chantier ; le budget est un texte décimal en euros."""

    model_config = CONFIG_ENTREE

    nom: str = Field(max_length=LONGUEUR_NOM_MAX)
    adresse: AdresseRequete
    client: str = Field(max_length=LONGUEUR_CLIENT_MAX)
    date_debut: date
    echeance: date
    # Les bornes sont celles de la colonne : un montant trop long est refusé ici, par un 422
    # sur le champ `budget`, avant d'atteindre le domaine.
    budget: MontantTexte = Field(max_digits=CHIFFRES_MONTANT_MAX, decimal_places=DECIMALES_MONTANT)


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
