"""Schémas JSON des routes des étapes : ce que l'API reçoit et ce qu'elle renvoie."""

from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

CONFIG_ENTREE = ConfigDict(extra="forbid", frozen=True, str_strip_whitespace=True)
CONFIG_SORTIE = ConfigDict(extra="forbid", frozen=True)

LONGUEUR_TITRE_MAX = 200
LONGUEUR_COMMENTAIRE_MAX = 1000

# Les valeurs du cycle d'une étape, telles que l'API les expose : elles typent le
# client TypeScript généré. L'api n'importe pas le domaine (contrat `api-sans-domain`),
# elles sont donc répétées ici ; le test du parcours complet les traverse toutes.
StatutReponse = Literal["a_faire", "en_cours", "terminee_a_valider", "validee"]
ActionEtape = Literal["demarrer", "signaler_terminee", "valider", "refuser"]


class AjouterEtapeRequete(BaseModel):
    """Corps de l'ajout d'une étape en fin de liste."""

    model_config = CONFIG_ENTREE

    titre: str = Field(max_length=LONGUEUR_TITRE_MAX)


class TransitionRequete(BaseModel):
    """Corps d'un changement de statut ; le commentaire est obligatoire pour `refuser`."""

    model_config = CONFIG_ENTREE

    action: ActionEtape
    commentaire: str | None = Field(default=None, max_length=LONGUEUR_COMMENTAIRE_MAX)


class EtapeReponse(BaseModel):
    """Étape telle que la voit l'acteur, avec les actions qu'il peut faire maintenant.

    Le frontend n'affiche que les boutons de `actions_permises`. `version` augmente
    à chaque transition.
    """

    model_config = CONFIG_SORTIE

    id: UUID
    chantier_id: UUID
    titre: str
    ordre: int
    statut: StatutReponse
    version: int
    actions_permises: list[ActionEtape]
