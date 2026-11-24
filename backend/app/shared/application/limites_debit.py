"""Seuils de la limite de débit et durée du blocage après un piège (lot S6).

Ce sont les décisions du propriétaire pour protéger la démo publique, où
l'écriture est ouverte à tous (`docs/plan/journal/lot-S6.md`). La composition
root les injecte dans les implémentations de `LimiteurDebit` et de
`ListeAdressesBloquees` (`ports.py`) : aucune autre couche ne les recopie.
"""

from datetime import timedelta

# Fenêtre de temps sur laquelle les accès d'une adresse sont comptés.
FENETRE_DEBIT = timedelta(minutes=1)

# Écritures permises par fenêtre et par adresse : assez pour remplir un formulaire
# à la main plusieurs fois par minute, trop peu pour remplir la base en masse.
ECRITURES_PAR_FENETRE = 20

# Lectures permises par fenêtre et par adresse : une page de l'interface en
# déclenche plusieurs à la fois, le seuil est donc bien plus large.
LECTURES_PAR_FENETRE = 120

# Durée pendant laquelle une adresse qui a touché un piège ne peut plus écrire.
DUREE_BLOCAGE_PIEGE = timedelta(hours=1)
