"""Vues des chantiers : ce que les cas d'usage renvoient, à la place des entités.

La vue est construite pour un acteur : elle ne contient que ce qu'il a le droit
de voir, et les actions qu'il a le droit de faire. Le frontend affiche, sans
jamais recalculer une règle (règle 02).
"""

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from uuid import UUID

from app.chantiers.application.ports import ResumeEtapes
from app.chantiers.domain.chantier import Chantier
from app.chantiers.domain.delai import calculer_delai
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
    `avancement` est un pourcentage entier de 0 à 100 ; les trois compteurs
    `etapes_*` viennent du module étapes (`ResumeEtapes`).
    `jours_restants` est toujours positif ou nul : c'est le nombre de jours avant
    l'échéance, ou, quand `en_retard` est vrai, le nombre de jours de retard
    (voir `Delai`). Les deux sont calculés à la date du jour, jamais stockés.
    """

    id: UUID
    nom: str
    adresse: AdresseVue
    client: str
    date_debut: date
    echeance: date
    budget: Decimal | None
    avancement: int
    etapes_validees: int
    etapes_total: int
    etapes_a_valider: int
    jours_restants: int
    en_retard: bool
    peut_ajouter_etape: bool


def vue_chantier(
    chantier: Chantier, acteur: Acteur, resume: ResumeEtapes, aujourd_hui: date
) -> ChantierVue:
    """Construit la vue d'un chantier pour un acteur, d'après les règles du domaine.

    Le délai est calculé par le domaine à partir de `aujourd_hui`, que le cas
    d'usage obtient du port `Horloge` : la vue ne lit jamais l'heure elle-même.
    """
    adresse = chantier.adresse
    delai = calculer_delai(chantier.echeance, aujourd_hui)
    return ChantierVue(
        id=chantier.id,
        nom=chantier.nom,
        adresse=AdresseVue(voie=adresse.voie, code_postal=adresse.code_postal, ville=adresse.ville),
        client=chantier.client,
        date_debut=chantier.date_debut,
        echeance=chantier.echeance,
        budget=chantier.budget.valeur if peut_voir_budget(acteur) else None,
        avancement=resume.avancement,
        etapes_validees=resume.validees,
        etapes_total=resume.total,
        etapes_a_valider=resume.a_valider,
        jours_restants=delai.jours_restants,
        en_retard=delai.en_retard,
        peut_ajouter_etape=peut_ajouter_etape(acteur),
    )
