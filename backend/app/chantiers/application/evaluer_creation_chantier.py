"""Cas d'usage public : dire si un acteur peut créer un chantier, pour un autre module."""

from app.chantiers.domain.politiques import peut_creer_chantier
from app.shared.domain.acteur import Acteur


class EvaluerCreationChantier:
    """Dit si l'acteur a le droit de créer un chantier, sans rien lire ni modifier.

    Utilisé par étapes pour annoncer les capacités de l'acteur au tableau de bord
    (`ConsulterCapacites`) : le droit porte sur les chantiers, il est donc décidé
    ici, par la politique du domaine, et étapes ne fait que le relayer. Le
    frontend affiche ainsi le lien « Nouveau chantier » sans déduire le droit du
    profil. La création elle-même revérifie le droit (`CreerChantier`).
    """

    def executer(self, acteur: Acteur) -> bool:
        """Renvoie vrai si la politique du domaine autorise l'acteur à créer un chantier."""
        return peut_creer_chantier(acteur)
