"""Entité `Etape` : une étape d'un chantier, qui suit le cycle décrit dans `cycle.py`.

Une étape ne référence son chantier que par son identifiant : le chantier est un
autre agrégat, géré par un autre module (règle 01).
"""

from collections.abc import Sequence
from dataclasses import dataclass, field
from datetime import datetime
from typing import Self
from uuid import UUID

from app.etapes.domain.cycle import ActionEtape, StatutEtape, trouver_transition
from app.shared.domain.acteur import Acteur, Role
from app.shared.domain.erreurs import ValeurInvalideError

PREMIER_ORDRE = 1
VERSION_INITIALE = 1


@dataclass
class HistoriqueEtape:
    """Trace d'une transition : qui (le rôle), quoi (les deux statuts), quand, et pourquoi.

    Dans le squelette, « qui » est le profil choisi dans l'interface, faute de compte
    utilisateur (docs/plan/squelette.md). Une entrée n'est jamais modifiée après sa
    création ; elle n'est pourtant pas figée, car le mapping impératif de SQLAlchemy
    doit pouvoir y attacher son état (règle 01, ADR 0002).
    """

    role: Role
    ancien_statut: StatutEtape
    nouveau_statut: StatutEtape
    date: datetime
    commentaire: str | None


@dataclass
class Etape:
    """Étape d'un chantier, dont le statut ne change que par `appliquer`.

    `version` sert de verrou optimiste : elle augmente à chaque transition, pour que
    deux actions simultanées sur la même étape ne s'écrasent pas (intent.md, §2.3).
    """

    id: UUID
    chantier_id: UUID
    titre: str
    ordre: int
    statut: StatutEtape = StatutEtape.A_FAIRE
    version: int = VERSION_INITIALE
    historique: list[HistoriqueEtape] = field(default_factory=list)

    @classmethod
    def creer(cls, id: UUID, chantier_id: UUID, titre: str, ordre: int) -> Self:
        """Crée une étape « À faire », sans historique : l'historique ne trace que les transitions.

        Lève :
            ValeurInvalideError : le titre est vide ou ne contient que des espaces.
        """
        if not titre.strip():
            raise ValeurInvalideError("Le titre de l'étape est obligatoire.")
        return cls(id=id, chantier_id=chantier_id, titre=titre, ordre=ordre)

    def appliquer(
        self,
        action: ActionEtape,
        acteur: Acteur,
        maintenant: datetime,
        commentaire: str | None = None,
    ) -> None:
        """Fait passer l'étape au statut prévu par la table, et trace la transition.

        Tout est vérifié avant la moindre modification : en cas d'erreur, l'étape
        reste exactement dans son état précédent.

        Lève :
            TransitionInterditeError : l'action n'est pas permise à ce rôle depuis ce statut.
            ValeurInvalideError : la transition exige un commentaire, absent ou vide.
        """
        transition = trouver_transition(self.statut, action, acteur.role)
        if transition.commentaire_obligatoire and not (commentaire and commentaire.strip()):
            raise ValeurInvalideError("Un commentaire est obligatoire pour cette action.")
        self.historique.append(
            HistoriqueEtape(
                role=acteur.role,
                ancien_statut=self.statut,
                nouveau_statut=transition.arrivee,
                date=maintenant,
                commentaire=commentaire,
            )
        )
        self.statut = transition.arrivee
        self.version += 1


def ordre_suivant(etapes: Sequence[Etape]) -> int:
    """Renvoie l'ordre d'une étape ajoutée en fin de liste.

    On part du plus grand ordre existant, et non du nombre d'étapes, pour rester
    juste quand des étapes seront supprimées (phase 2).
    """
    return max((etape.ordre for etape in etapes), default=PREMIER_ORDRE - 1) + 1
