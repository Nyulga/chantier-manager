"""Garde des plafonds de volume, commune aux cas d'usage qui créent des objets."""

from app.shared.application.erreurs import PlafondAtteintError


def exiger_place_sous_le_plafond(existants: int, plafond: int, message: str) -> None:
    """Refuse une création quand le nombre d'objets `existants` a déjà atteint `plafond`.

    La garde est appelée dans la transaction de la création, avant toute écriture :
    le refus ne laisse donc rien derrière lui. `message` est affiché tel quel à
    l'acteur ; il nomme le plafond, sans aucune donnée personnelle.

    Lève :
        PlafondAtteintError : `existants` est égal ou supérieur à `plafond`.
    """
    if existants >= plafond:
        raise PlafondAtteintError(message)
