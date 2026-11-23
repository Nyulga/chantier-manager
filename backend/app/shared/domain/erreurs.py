"""Erreurs métier communes à tous les modules.

L'api les traduit en codes HTTP à un seul endroit ; les services les laissent
remonter sans les masquer (règle 02). Leurs messages sont en français et ne
contiennent jamais de donnée personnelle, car ils peuvent être affichés.
"""

# Message commun aux conflits de modification, affiché tel quel à l'acteur : recharger
# l'écran suffit à voir l'état que l'autre personne vient d'enregistrer.
MESSAGE_MODIFIE_ENTRE_TEMPS = (
    "Cet élément vient d'être modifié par quelqu'un d'autre : recharge la page."
)


class ErreurMetierError(Exception):
    """Classe de base de toute erreur métier : une règle du domaine a été enfreinte."""


class NonTrouveError(ErreurMetierError):
    """L'objet demandé n'existe pas, ou l'acteur n'a pas le droit de savoir qu'il existe."""


class TransitionInterditeError(ErreurMetierError):
    """L'action demandée n'est pas permise depuis l'état actuel de l'objet, pour ce rôle."""


class ValeurInvalideError(ErreurMetierError):
    """Une valeur ne respecte pas un invariant du domaine : l'objet ne peut pas exister.

    `champ` désigne, quand on le sait, le champ de saisie fautif, écrit comme l'api
    l'expose (`"nom"`, `"adresse.voie"`) : l'écran peut alors afficher le message
    sous ce champ. Il reste `None` quand l'erreur porte sur plusieurs champs à la
    fois, ou sur une valeur qui ne vient pas d'un champ.
    """

    def __init__(self, message: str, champ: str | None = None) -> None:
        super().__init__(message)
        self.champ = champ


class AccesRefuseError(ErreurMetierError):
    """L'acteur connaît l'objet, mais son rôle ne l'autorise pas à faire cette action."""


class ConflitVersionError(ErreurMetierError):
    """L'objet a été modifié par quelqu'un d'autre depuis sa lecture : l'action est rejetée.

    C'est le verrou optimiste (intent.md, §2.3) : de deux actions simultanées sur
    le même objet, la seconde est refusée plutôt que d'écraser la première.
    """
