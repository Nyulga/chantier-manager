"""Schémas JSON des routes des étapes : ce que l'API reçoit et ce qu'elle renvoie."""

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field

from app.etapes.application.valeurs_publiques import (
    LONGUEUR_COMMENTAIRE_MAX,
    LONGUEUR_TITRE_MAX,
    VERSION_INITIALE,
    Role,
)
from app.shared.api.champ_piege import ChampPiege
from app.shared.api.schemas import CONFIG_ENTREE, CONFIG_SORTIE

# Les valeurs du cycle d'une étape, telles que l'API les expose : elles typent le
# client TypeScript généré. L'api n'importe pas le domaine (contrat `api-sans-domain`),
# elles sont donc répétées ici ; `test_parite_schemas_et_domaine.py` les compare aux
# énumérations du domaine. Les rôles, eux, viennent de `Role` par la couche application
# (`valeurs_publiques.py`) : ils n'ont pas de copie.
StatutReponse = Literal["a_faire", "en_cours", "terminee_a_valider", "validee"]
ActionEtape = Literal["demarrer", "signaler_terminee", "valider", "refuser"]


class AjouterEtapeRequete(ChampPiege):
    """Corps de l'ajout d'une étape en fin de liste."""

    model_config = CONFIG_ENTREE

    titre: str = Field(max_length=LONGUEUR_TITRE_MAX)


class TransitionRequete(BaseModel):
    """Corps d'un changement de statut ; le commentaire est facultatif, sauf pour `refuser`.

    `version` est la version de l'étape que l'écran affichait. Si l'étape a changé depuis,
    l'action est refusée (409) plutôt que décidée sur un état périmé. Sans version, l'action
    s'applique à l'étape telle qu'elle est.
    """

    model_config = CONFIG_ENTREE

    action: ActionEtape
    commentaire: str | None = Field(default=None, max_length=LONGUEUR_COMMENTAIRE_MAX)
    version: int | None = Field(default=None, ge=VERSION_INITIALE)


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
    role: Role
    ancien_statut: StatutReponse
    nouveau_statut: StatutReponse
    date: datetime
    commentaire: str | None


class CapacitesReponse(BaseModel):
    """Ce que l'acteur peut faire, d'après son profil : l'écran n'en déduit rien lui-même.

    `peut_creer_chantier` commande le lien « Nouveau chantier », et
    `peut_lister_etapes_a_valider` le bloc « À valider » du tableau de bord.
    """

    model_config = CONFIG_SORTIE

    role: Role
    peut_creer_chantier: bool
    peut_lister_etapes_a_valider: bool
