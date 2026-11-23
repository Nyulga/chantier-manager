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
from app.shared.domain.longueur import exiger_longueur_max

# Bornes de saisie du nom et du client : assez larges pour tout intitulé réel,
# elles empêchent qu'un texte démesuré soit enregistré puis affiché sur chaque
# carte. L'api et les colonnes de la base s'y réfèrent.
LONGUEUR_NOM_MAX = 200
LONGUEUR_CLIENT_MAX = 200


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
            ValeurInvalideError : le nom ou le client est vide ou trop long, ou
                l'échéance précède la date de début.
        """
        if not self.nom.strip():
            raise ValeurInvalideError("Le nom du chantier est obligatoire.", "nom")
        exiger_longueur_max(self.nom, LONGUEUR_NOM_MAX, "Le nom du chantier", "nom")
        # Un chantier se fait toujours pour un client : sans lui, la fiche est inexploitable.
        if not self.client.strip():
            raise ValeurInvalideError("Le client du chantier est obligatoire.", "client")
        exiger_longueur_max(self.client, LONGUEUR_CLIENT_MAX, "Le client du chantier", "client")
        # Une échéance le jour même du début reste possible : c'est le cas d'un
        # chantier d'une seule journée.
        if self.echeance < self.date_debut:
            raise ValeurInvalideError(
                "L'échéance ne peut pas précéder la date de début.", "echeance"
            )


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
