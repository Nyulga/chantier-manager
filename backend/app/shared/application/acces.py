"""Garde d'accès commune aux cas d'usage : traduit le refus d'une politique en erreur."""

from app.shared.domain.erreurs import AccesRefuseError


def exiger_acces(*, autorise: bool, message: str) -> None:
    """Lève `AccesRefuseError` quand la politique du domaine a refusé l'action.

    Les politiques sont des fonctions pures qui renvoient un booléen et ne lèvent
    rien (règle 01) ; c'est le cas d'usage qui transforme leur refus en erreur. La
    garde le fait à un seul endroit, avec le même type d'erreur partout. Elle
    permet aussi d'appeler une politique encore vraie pour tous les rôles, comme
    celle du fil d'activité dans le squelette, sans laisser dans le cas d'usage
    une branche de refus impossible à atteindre.

    Lève :
        AccesRefuseError : `autorise` est faux ; l'erreur porte `message`, qui ne
            doit contenir aucune donnée personnelle.
    """
    if not autorise:
        raise AccesRefuseError(message)
