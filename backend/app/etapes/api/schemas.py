"""Schémas JSON des routes des étapes : ce que l'API reçoit et ce qu'elle renvoie."""

from datetime import datetime
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
RoleReponse = Literal["chef", "ouvrier"]


class AjouterEtapeRequete(BaseModel):
    """Corps de l'ajout d'une étape en fin de liste."""

    model_config = CONFIG_ENTREE

    titre: str = Field(max_length=LONGUEUR_TITRE_MAX)


class TransitionRequete(BaseModel):
    """Corps d'un changement de statut ; le commentaire est facultatif, sauf pour `refuser`."""

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


class EtapeAValiderReponse(BaseModel):
    """Étape qui attend la décision d'un chef, telle qu'elle figure dans « À valider ».

    La liste va de l'étape signalée depuis le plus longtemps à la plus récente.
    `signalee_le` est la date du dernier signalement « terminée » (après un refus,
    c'est le nouveau qui compte) ; elle n'est `null` que sur une donnée incohérente.
    """

    model_config = CONFIG_SORTIE

    id: UUID
    chantier_id: UUID
    titre: str
    version: int
    actions_permises: list[ActionEtape]
    signalee_le: datetime | None


class ActiviteReponse(BaseModel):
    """Une entrée du fil d'activité : un changement de statut d'une étape.

    `role` est le profil qui a agi. `commentaire` est facultatif sur toute
    transition, et toujours renseigné pour un refus, où il est obligatoire.
    """

    model_config = CONFIG_SORTIE

    etape_id: UUID
    chantier_id: UUID
    titre_etape: str
    role: RoleReponse
    ancien_statut: StatutReponse
    nouveau_statut: StatutReponse
    date: datetime
    commentaire: str | None
