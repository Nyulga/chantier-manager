"""Agrégat `Chantier` et sa fiche descriptive.

Les invariants sont portés par `FicheChantier`, que l'on construit avant le
chantier : un chantier ne peut donc naître que d'informations déjà valides.
"""

from dataclasses import dataclass
from datetime import date
from typing import Self
from uuid import UUID

from app.chantiers.domain.adresse import Adresse
from app.chantiers.domain.montant import Montant
from app.shared.domain.erreurs import ValeurInvalideError


@dataclass(frozen=True, slots=True)
class FicheChantier:
    """Informations descriptives d'un chantier, validées ensemble.

    Elles sont regroupées parce que l'invariant sur les dates porte sur deux champs
    à la fois, et pour que la fabrique `Chantier.creer` reste lisible. La
    modification d'un chantier, en phase 2, pourra réutiliser la même fiche.
    """

    nom: str
    adresse: Adresse
    client: str
    date_debut: date
    echeance: date
    budget: Montant

    def __post_init__(self) -> None:
        """Refuse une fiche qui viole un invariant du chantier.

        Lève :
            ValeurInvalideError : le nom est vide, ou l'échéance précède la date de début.
        """
        if not self.nom.strip():
            raise ValeurInvalideError("Le nom du chantier est obligatoire.")
        # Une échéance le jour même du début reste possible : c'est le cas d'un
        # chantier d'une seule journée.
        if self.echeance < self.date_debut:
            raise ValeurInvalideError("L'échéance ne peut pas précéder la date de début.")


@dataclass
class Chantier:
    """Chantier suivi par l'application : racine de son agrégat.

    Les autres agrégats, comme les étapes, ne le référencent que par son
    identifiant (règle 01). Dans le squelette, un chantier ne se modifie pas encore ;
    sa modification et son archivage sont reportés (docs/plan/squelette.md).
    """

    id: UUID
    nom: str
    adresse: Adresse
    client: str
    date_debut: date
    echeance: date
    budget: Montant

    @classmethod
    def creer(cls, id: UUID, fiche: FicheChantier) -> Self:
        """Crée un chantier à partir d'une fiche, valide par construction.

        L'identifiant est fourni par l'appelant, qui l'obtient du port
        `GenerateurId` : le domaine ne produit aucune valeur non déterministe.
        """
        return cls(
            id=id,
            nom=fiche.nom,
            adresse=fiche.adresse,
            client=fiche.client,
            date_debut=fiche.date_debut,
            echeance=fiche.echeance,
            budget=fiche.budget,
        )
