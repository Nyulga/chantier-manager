"""Vue d'une étape : ce que les cas d'usage renvoient, à la place de l'entité.

Les statuts et les actions y sont des chaînes (`"en_cours"`, `"valider"`) : l'api
ne connaît pas le domaine (contrat import-linter `api-sans-domain`).
"""

from dataclasses import dataclass
from uuid import UUID

from app.etapes.domain.cycle import actions_permises
from app.etapes.domain.etape import Etape
from app.shared.domain.acteur import Acteur


@dataclass(frozen=True)
class EtapeVue:
    """Étape vue par un acteur, avec les actions qu'il peut faire maintenant.

    `actions_permises` vient directement de la table des transitions : le frontend
    n'affiche que ces boutons, sans recalculer le cycle. `version` permettra de
    détecter deux modifications simultanées (intent.md, §2.3).
    """

    id: UUID
    chantier_id: UUID
    titre: str
    ordre: int
    statut: str
    version: int
    actions_permises: tuple[str, ...]


def vue_etape(etape: Etape, acteur: Acteur) -> EtapeVue:
    """Construit la vue d'une étape pour un acteur."""
    return EtapeVue(
        id=etape.id,
        chantier_id=etape.chantier_id,
        titre=etape.titre,
        ordre=etape.ordre,
        statut=etape.statut.value,
        version=etape.version,
        actions_permises=tuple(
            action.value for action in actions_permises(etape.statut, acteur.role)
        ),
    )
