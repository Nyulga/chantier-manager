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
from app.shared.domain.erreurs import ConflitVersionError, ValeurInvalideError
from app.shared.domain.longueur import exiger_longueur_max

PREMIER_ORDRE = 1
VERSION_INITIALE = 1
# Bornes de saisie du titre et du commentaire : assez larges pour décrire une étape
# ou ce qu'il faut reprendre, elles empêchent qu'un texte démesuré soit enregistré
# puis affiché dans chaque liste. L'api et les colonnes de la base s'y réfèrent.
LONGUEUR_TITRE_MAX = 200
LONGUEUR_COMMENTAIRE_MAX = 1000


@dataclass
class HistoriqueEtape:
    """Trace d'une transition : qui (le rôle), quoi (les deux statuts), quand, et pourquoi.

    Dans le squelette, « qui » est le profil choisi dans l'interface, faute de compte
    utilisateur (docs/plan/squelette.md). Le commentaire est facultatif sur toute
    transition, et obligatoire pour un refus (voir `Transition`). Une entrée n'est
    jamais modifiée après sa création ; elle n'est pourtant pas figée, car le mapping
    impératif de SQLAlchemy doit pouvoir y attacher son état (règle 01, ADR 0002).
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
            ValeurInvalideError : le titre est vide, ne contient que des espaces, ou
                dépasse `LONGUEUR_TITRE_MAX` caractères.
        """
        if not titre.strip():
            raise ValeurInvalideError("Le titre de l'étape est obligatoire.", "titre")
        exiger_longueur_max(titre, LONGUEUR_TITRE_MAX, "Le titre de l'étape", "titre")
        return cls(id=id, chantier_id=chantier_id, titre=titre, ordre=ordre)

    def appliquer(
        self,
        action: ActionEtape,
        acteur: Acteur,
        maintenant: datetime,
        commentaire: str | None = None,
    ) -> None:
        """Fait passer l'étape au statut prévu par la table, et trace la transition.

        Le commentaire est facultatif, sauf quand la transition l'exige (le refus).
        Tout est vérifié avant la moindre modification : en cas d'erreur, l'étape
        reste exactement dans son état précédent.

        Lève :
            TransitionInterditeError : l'action n'est pas permise à ce rôle depuis ce statut.
            ValeurInvalideError : la transition exige un commentaire, absent ou vide, ou
                le commentaire dépasse `LONGUEUR_COMMENTAIRE_MAX` caractères.
        """
        transition = trouver_transition(self.statut, action, acteur.role)
        if transition.commentaire_obligatoire and not (commentaire and commentaire.strip()):
            raise ValeurInvalideError(
                "Un commentaire est obligatoire pour cette action.", "commentaire"
            )
        if commentaire is not None:
            exiger_longueur_max(
                commentaire, LONGUEUR_COMMENTAIRE_MAX, "Le commentaire", "commentaire"
            )
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

    def verifier_version(self, version_attendue: int | None) -> None:
        """Refuse d'agir sur une étape qui a changé depuis que l'acteur l'a vue.

        Le client renvoie la version qu'il affichait. Si elle diffère de la version
        actuelle, quelqu'un a fait avancer l'étape entre-temps : appliquer l'action
        reviendrait à décider sur un état périmé (intent.md, §2.3). Sans version
        attendue, rien n'est vérifié ici ; le verrou optimiste de la transaction
        protège encore des écritures vraiment simultanées.

        Lève :
            ConflitVersionError : la version attendue n'est pas la version actuelle.
        """
        if version_attendue is not None and version_attendue != self.version:
            raise ConflitVersionError(
                "Cette étape vient d'être modifiée par quelqu'un d'autre : recharge la page."
            )

    def signalee_le(self) -> datetime | None:
        """Renvoie la date du dernier signalement de l'étape comme terminée.

        C'est la plus récente transition vers « Terminée (à valider) » : après un
        refus, l'étape est signalée de nouveau, et c'est ce nouveau signalement que
        le chef doit traiter. Renvoie `None` si l'historique n'en garde aucun.
        """
        dates = [
            entree.date
            for entree in self.historique
            if entree.nouveau_statut is StatutEtape.TERMINEE_A_VALIDER
        ]
        return max(dates, default=None)


def ordre_suivant(etapes: Sequence[Etape]) -> int:
    """Renvoie l'ordre d'une étape ajoutée en fin de liste.

    On part du plus grand ordre existant, et non du nombre d'étapes, pour rester
    juste quand des étapes seront supprimées (phase 2).
    """
    return max((etape.ordre for etape in etapes), default=PREMIER_ORDRE - 1) + 1


def trier_par_signalement(etapes: Sequence[Etape]) -> list[Etape]:
    """Trie des étapes de la plus anciennement signalée à la plus récente.

    L'étape qui attend depuis le plus longtemps passe en premier : c'est elle que
    le chef doit traiter d'abord. Une étape sans signalement connu (une donnée
    incohérente, que le cycle ne produit pas) passe en tête, pour ne jamais rester
    cachée en bas de la liste. À date égale, l'identifiant, croissant comme l'ordre
    de création des UUID v7, départage les étapes : le tri reste ainsi stable.
    """
    return sorted(etapes, key=_cle_de_signalement)


def _cle_de_signalement(etape: Etape) -> tuple[bool, datetime | None, UUID]:
    """Clé de tri : d'abord les étapes sans date, puis par date, puis par identifiant.

    Deux étapes sans date ont le même premier et le même deuxième élément : Python
    passe alors directement à l'identifiant, sans jamais comparer `None` à `None`.
    """
    date_signalement = etape.signalee_le()
    return (date_signalement is not None, date_signalement, etape.id)
