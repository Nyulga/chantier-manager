"""Vues des étapes : ce que les cas d'usage renvoient, à la place des entités.

Les statuts, les rôles et les actions y sont des chaînes (`"en_cours"`, `"chef"`,
`"valider"`) : l'api ne connaît pas le domaine (contrat import-linter `api-sans-domain`).
"""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from app.etapes.domain.avancement import ResumeEtapes
from app.etapes.domain.cycle import actions_permises
from app.etapes.domain.etape import Etape, HistoriqueEtape
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


@dataclass(frozen=True)
class EtapeAValiderVue:
    """Étape en attente de la décision d'un chef, telle qu'elle figure dans « À valider ».

    `signalee_le` est la date du dernier signalement « terminée » : après un refus,
    c'est le nouveau signalement qui compte. Elle ne vaut `None` que pour une étape
    dont l'historique ne garde aucun signalement, ce que l'application ne produit
    jamais (chaque transition est tracée) ; le type le prévoit pour une donnée incohérente.
    """

    id: UUID
    chantier_id: UUID
    titre: str
    version: int
    actions_permises: tuple[str, ...]
    signalee_le: datetime | None


@dataclass(frozen=True)
class ActiviteVue:
    """Une entrée du fil d'activité : un changement de statut d'une étape.

    `role` est le profil qui a agi : dans le squelette, il n'y a pas encore de
    compte utilisateur (docs/plan/squelette.md).
    """

    etape_id: UUID
    chantier_id: UUID
    titre_etape: str
    role: str
    ancien_statut: str
    nouveau_statut: str
    date: datetime
    commentaire: str | None


@dataclass(frozen=True)
class CapacitesVue:
    """Ce que l'acteur peut faire, indépendamment d'un chantier ou d'une étape précis.

    `role` est le profil de l'acteur (`"chef"` ou `"ouvrier"`), pour l'affichage.
    Les deux booléens sont calculés par les politiques du domaine : le frontend
    n'affiche le lien de création et le bloc « À valider » que s'ils sont vrais.
    """

    role: str
    peut_creer_chantier: bool
    peut_lister_etapes_a_valider: bool


@dataclass(frozen=True)
class ResumeEtapesVue:
    """Résumé des étapes d'un chantier, publié pour le module chantiers.

    `avancement` est un pourcentage entier de 0 à 100. La composition root le
    traduit dans le type que chantiers attend, sans que l'un importe l'autre.
    """

    avancement: int
    validees: int
    total: int
    a_valider: int


def _actions(etape: Etape, acteur: Acteur) -> tuple[str, ...]:
    """Liste les noms des actions que l'acteur peut faire sur l'étape, d'après la table."""
    return tuple(action.value for action in actions_permises(etape.statut, acteur.role))


def vue_etape(etape: Etape, acteur: Acteur) -> EtapeVue:
    """Construit la vue d'une étape pour un acteur."""
    return EtapeVue(
        id=etape.id,
        chantier_id=etape.chantier_id,
        titre=etape.titre,
        ordre=etape.ordre,
        statut=etape.statut.value,
        version=etape.version,
        actions_permises=_actions(etape, acteur),
    )


def vue_etape_a_valider(etape: Etape, acteur: Acteur) -> EtapeAValiderVue:
    """Construit la vue d'une étape à valider pour un acteur."""
    return EtapeAValiderVue(
        id=etape.id,
        chantier_id=etape.chantier_id,
        titre=etape.titre,
        version=etape.version,
        actions_permises=_actions(etape, acteur),
        signalee_le=etape.signalee_le(),
    )


def vue_activite(etape: Etape, entree: HistoriqueEtape) -> ActiviteVue:
    """Construit l'entrée du fil d'activité qui correspond à une transition de l'étape."""
    return ActiviteVue(
        etape_id=etape.id,
        chantier_id=etape.chantier_id,
        titre_etape=etape.titre,
        role=entree.role.value,
        ancien_statut=entree.ancien_statut.value,
        nouveau_statut=entree.nouveau_statut.value,
        date=entree.date,
        commentaire=entree.commentaire,
    )


def vue_resume(resume: ResumeEtapes) -> ResumeEtapesVue:
    """Construit la vue publique d'un résumé d'étapes."""
    return ResumeEtapesVue(
        avancement=resume.avancement,
        validees=resume.validees,
        total=resume.total,
        a_valider=resume.a_valider,
    )
