# Journal du lot S6 – Sécuriser la démo

**Issue** : #45 · **Statut** : en cours depuis le 2026-11-24 · **Plage** : `ee4b35a..`

Le lot fait suite au premier test d'intrusion local (règle 08) et à la demande du propriétaire de protéger la démo publique, où l'écriture est ouverte à tous. Le plan a été validé par le propriétaire le 2026-11-24.

## Décisions du propriétaire

- **Limites de débit** : 20 écritures et 120 lectures par minute et par adresse ; une adresse qui touche un piège est bloquée en écriture pendant 1 heure.
- **Plafonds de volume** : 100 chantiers en tout, 30 étapes par chantier. La démo n'est **pas** remise à zéro : une fois le plafond atteint, plus aucune création n'est possible, et le propriétaire décidera de la suite.
- **Mise en ligne** : étape séparée, après le lot, avec accord pour chaque commande sur le serveur (le bloc Caddy du serveur change).
- **Hors lot** : fail2ban sur le serveur (lot 08) ; le code d'erreur d'un ouvrier qui tente de valider (issue à part).
