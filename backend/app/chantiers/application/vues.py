"""Vues des chantiers : ce que les cas d'usage renvoient, à la place des entités.

La vue est construite pour un acteur : elle ne contient que ce qu'il a le droit
de voir, et les actions qu'il a le droit de faire. Le frontend affiche, sans
jamais recalculer une règle (règle 02).
"""

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from uuid import UUID

from app.chantiers.domain.chantier import Chantier
from app.chantiers.domain.politiques import peut_ajouter_etape, peut_voir_budget
from app.shared.domain.acteur import Acteur


@dataclass(frozen=True)
class AdresseVue:
    """Adresse d'un chantier, telle qu'elle est affichée."""

    voie: str
    code_postal: str
    ville: str


@dataclass(frozen=True)
class ChantierVue:
    """Chantier vu par un acteur.

    `budget` est en euros, et vaut `None` quand l'acteur n'a pas le droit de le voir :
    l'information n'est pas masquée par l'interface, elle n'est jamais envoyée.
    `avancement` est un pourcentage entier de 0 à 100.
    """

    id: UUID
    nom: str
    adresse: AdresseVue
    client: str
    date_debut: date
    echeance: date
    budget: Decimal | None
    avancement: int
    peut_ajouter_etape: bool


def vue_chantier(chantier: Chantier, acteur: Acteur, avancement: int) -> ChantierVue:
    """Construit la vue d'un chantier pour un acteur, d'après les politiques du domaine."""
    adresse = chantier.adresse
    return ChantierVue(
        id=chantier.id,
        nom=chantier.nom,
        adresse=AdresseVue(voie=adresse.voie, code_postal=adresse.code_postal, ville=adresse.ville),
        client=chantier.client,
        date_debut=chantier.date_debut,
        echeance=chantier.echeance,
        budget=chantier.budget.valeur if peut_voir_budget(acteur) else None,
        avancement=avancement,
        peut_ajouter_etape=peut_ajouter_etape(acteur),
    )
