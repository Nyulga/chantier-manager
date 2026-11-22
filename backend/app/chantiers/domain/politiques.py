"""Politiques d'accès du module chantiers : des fonctions pures qui ne lèvent rien.

Dans le squelette, il n'y a pas encore d'affectation : les droits ne dépendent que
du rôle. En phase 2, ces fonctions recevront aussi le chantier, pour vérifier que
l'acteur y est affecté (intent.md, §1, cloisonnement).
"""

from app.shared.domain.acteur import Acteur, Role


def peut_creer_chantier(acteur: Acteur) -> bool:
    """Seul un chef crée des chantiers : un ouvrier ne fait que suivre ceux qu'on lui confie."""
    return acteur.role is Role.CHEF


def peut_voir_budget(acteur: Acteur) -> bool:
    """Seul un chef voit le budget : c'est une information commerciale (intent.md, §1)."""
    return acteur.role is Role.CHEF


def peut_ajouter_etape(acteur: Acteur) -> bool:
    """Seul un chef définit les étapes d'un chantier (intent.md, §1).

    Ce droit porte sur le chantier, c'est pourquoi il vit ici et non dans le module
    étapes : en phase 2, il dépendra de l'affectation au chantier.
    """
    return acteur.role is Role.CHEF
