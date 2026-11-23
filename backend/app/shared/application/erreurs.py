"""Erreurs de l'application : celles qui ne viennent pas d'une règle métier.

Les adaptateurs d'infrastructure y traduisent leurs erreurs techniques (règle 03) :
aucune exception de SQLAlchemy, du réseau ou du disque ne doit remonter jusqu'à l'api.
"""


class ServiceIndisponibleError(Exception):
    """Un service dont dépend l'application ne répond pas : base de données, antivirus…

    Ce n'est pas une erreur du domaine : l'acteur n'a rien fait de mal, et réessayer
    plus tard peut réussir. L'api la traduit en 503. Son message est technique et
    n'est jamais affiché : la cause d'origine reste chaînée (`__cause__`) pour le
    journal du serveur.
    """
