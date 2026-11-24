"""Ports transverses : l'heure, les identifiants, la transaction et la limite de débit.

Ce sont les seules sources non déterministes ou techniques dont le backend a
besoin. Elles arrivent par le constructeur, ce qui permet de les remplacer par
des fakes dans les tests (règle 02).

Les deux ports de la limite de débit (`LimiteurDebit`, `ListeAdressesBloquees`)
ne servent pas aux cas d'usage, mais aux middlewares de `shared/api` qui
protègent la démo publique (lot S6). Leurs valeurs (seuils, fenêtre, durée du
blocage) sont injectées dans les implémentations par la composition root ; elles
sont nommées dans `limites_debit.py`.
"""

from datetime import date, datetime
from enum import StrEnum
from types import TracebackType
from typing import Protocol, Self
from uuid import UUID


class Horloge(Protocol):
    """Donne l'heure courante : le domaine ne lit jamais l'horloge du système lui-même."""

    def maintenant(self) -> datetime:
        """Renvoie l'instant présent, avec son fuseau horaire."""
        ...

    def aujourd_hui(self) -> date:
        """Renvoie la date du jour à Paris, et non en UTC.

        C'est la date que vivent les utilisateurs : elle sert aux règles comptées en
        jours, comme le délai qui reste avant une échéance. La date UTC retarderait
        d'un jour entre minuit et 1 h (2 h en été), heure de Paris.
        """
        ...


class GenerateurId(Protocol):
    """Fournit les identifiants des nouveaux objets (UUID v7 en production, intent.md §2.3)."""

    def nouveau(self) -> UUID:
        """Renvoie un identifiant jamais encore attribué."""
        ...


class UnitOfWork(Protocol):
    """Transaction qui englobe tout un cas d'usage, utilisée comme gestionnaire de contexte.

    Les écritures ne sont conservées que si `valider()` a été appelée avant la
    sortie du bloc `with`. Toute sortie sans validation, en particulier à cause
    d'une exception, annule l'ensemble : on ne voit jamais un état à moitié écrit.
    Chaque module étend ce port pour y ajouter ses repositories.
    """

    def __enter__(self) -> Self:
        """Ouvre la transaction."""
        ...

    def __exit__(
        self,
        type_erreur: type[BaseException] | None,
        erreur: BaseException | None,
        trace: TracebackType | None,
    ) -> None:
        """Ferme la transaction, en l'annulant si elle n'a pas été validée."""
        ...

    def valider(self) -> None:
        """Valide la transaction ; un cas d'usage l'appelle une seule fois, à la fin."""
        ...


class CategorieAcces(StrEnum):
    """Nature d'un accès, comptée à part dans la limite de débit.

    Une écriture coûte plus cher qu'une lecture (elle remplit la base) et c'est elle
    qu'un robot cherche à répéter : elle a donc un seuil plus bas. Compter les deux
    séparément évite qu'une navigation normale épuise le droit d'écrire.
    """

    LECTURE = "lecture"
    ECRITURE = "ecriture"


class LimiteurDebit(Protocol):
    """Compte les accès de chaque adresse et refuse ceux qui dépassent le seuil.

    Le seuil de chaque catégorie et la fenêtre de temps sont fixés à la construction
    par la composition root (`limites_debit.py`), et l'heure vient du port `Horloge` :
    l'appelant n'a qu'à demander, sans connaître la règle.

    Hypothèse assumée pendant le squelette : l'implémentation garde ses compteurs en
    mémoire. Ils sont donc perdus au redémarrage et propres à un processus, ce qui
    suffit avec un seul conteneur API à un seul worker (ADR 0015). Elle doit rester
    juste sous des appels concurrents et oublier les entrées expirées, pour que sa
    mémoire ne grossisse pas sans fin.
    """

    def consommer(self, adresse: str, categorie: CategorieAcces) -> int | None:
        """Consomme une unité de `categorie` pour `adresse`, si le seuil le permet.

        Renvoie `None` quand l'accès est permis. Sinon, renvoie le nombre entier de
        secondes à attendre avant de réessayer, toujours au moins 1 : l'appelant le
        recopie tel quel dans l'en-tête `Retry-After`, sans arrondi à faire. Un accès
        refusé ne consomme rien ; le délai annoncé est ainsi exact : passé ce délai,
        le même accès est de nouveau permis. Les adresses et les catégories sont
        comptées indépendamment les unes des autres.
        """
        ...


class ListeAdressesBloquees(Protocol):
    """Retient les adresses privées d'écriture pour un temps, après un piège touché.

    Une adresse qui remplit le champ piège d'un formulaire ou qui demande une fausse
    adresse piège se conduit en robot : l'appelant la bloque, puis refuse ses
    écritures tant qu'elle l'est. Ses lectures restent permises, pour ne pas
    empêcher de consulter la démo une personne qui partage l'adresse du robot.

    La durée du blocage est fixée à la construction par la composition root
    (`DUREE_BLOCAGE_PIEGE`), et non passée à `bloquer` : tous les pièges ont la
    même sanction, et l'appelant n'a pas à la connaître. La même hypothèse que pour
    `LimiteurDebit` s'applique : liste en mémoire, perdue au redémarrage.
    """

    def bloquer(self, adresse: str) -> None:
        """Bloque `adresse` pour toute la durée, à partir de maintenant.

        Bloquer une adresse déjà bloquée fait repartir la durée de zéro : un robot
        qui insiste reste bloqué.
        """
        ...

    def est_bloquee(self, adresse: str) -> bool:
        """Indique si `adresse` est bloquée en ce moment (la durée n'est pas écoulée)."""
        ...
