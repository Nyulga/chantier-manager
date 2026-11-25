"""Erreurs de l'application : celles qui ne viennent pas d'une règle du domaine.

Les adaptateurs d'infrastructure y traduisent leurs erreurs techniques (règle 03) :
aucune exception de SQLAlchemy, du réseau ou du disque ne doit remonter jusqu'à l'api.
On y trouve aussi le refus d'un plafond de volume, décidé par la couche application.
"""

from app.shared.domain.erreurs import ErreurMetierError


class ServiceIndisponibleError(Exception):
    """Un service dont dépend l'application ne répond pas : base de données, antivirus…

    Ce n'est pas une erreur du domaine : l'acteur n'a rien fait de mal, et réessayer
    plus tard peut réussir. L'api la traduit en 503. Son message est technique et
    n'est jamais affiché : la cause d'origine reste chaînée (`__cause__`) pour le
    journal du serveur.
    """


class PlafondAtteintError(ErreurMetierError):
    """Une création est refusée parce que le plafond de volume est atteint.

    Les plafonds ne sont pas des règles du domaine : ce sont des limites de la
    démonstration publique, fixées dans les `plafonds.py` de la couche application.
    L'erreur hérite pourtant d'`ErreurMetierError`, car, comme une erreur métier, elle
    vient de la demande de l'acteur et non d'une panne : réessayer ne changera rien, et
    son message, en français et sans donnée personnelle, est écrit pour être affiché.
    """
