"""Erreurs métier communes à tous les modules.

L'api les traduit en codes HTTP à un seul endroit ; les services les laissent
remonter sans les masquer (règle 02). Leurs messages sont en français et ne
contiennent jamais de donnée personnelle, car ils peuvent être affichés.
"""


class ErreurMetierError(Exception):
    """Classe de base de toute erreur métier : une règle du domaine a été enfreinte."""


class NonTrouveError(ErreurMetierError):
    """L'objet demandé n'existe pas, ou l'acteur n'a pas le droit de savoir qu'il existe."""


class TransitionInterditeError(ErreurMetierError):
    """L'action demandée n'est pas permise depuis l'état actuel de l'objet, pour ce rôle."""


class ValeurInvalideError(ErreurMetierError):
    """Une valeur ne respecte pas un invariant du domaine : l'objet ne peut pas exister."""


class AccesRefuseError(ErreurMetierError):
    """L'acteur connaît l'objet, mais son rôle ne l'autorise pas à faire cette action."""


class ConflitVersionError(ErreurMetierError):
    """L'objet a été modifié par quelqu'un d'autre depuis sa lecture : l'action est rejetée.

    C'est le verrou optimiste (intent.md, §2.3) : de deux actions simultanées sur
    le même objet, la seconde est refusée plutôt que d'écraser la première.
    """
