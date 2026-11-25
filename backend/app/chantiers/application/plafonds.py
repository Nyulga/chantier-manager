"""Plafonds de volume du module chantiers : le nombre total de chantiers de la démo.

Ce n'est pas une règle métier : aucune règle du produit ne limite le nombre de
chantiers d'une entreprise. C'est une protection de la démonstration publique, où
l'écriture est ouverte à tous, sans compte : sans plafond, n'importe qui pourrait
remplir la base sans limite. La démo n'est pas remise à zéro : une fois le plafond
atteint, plus aucune création n'est possible, et le propriétaire décide de la suite
(décision du propriétaire, journal du lot S6). Le plafond vit donc dans la couche
application, à côté du cas d'usage qui l'applique, et non dans le domaine.
"""

# Nombre maximal de chantiers, tous chantiers confondus.
LIMITE_CHANTIERS = 100
MESSAGE_LIMITE_CHANTIERS = f"La démo a atteint sa limite de {LIMITE_CHANTIERS} chantiers."
