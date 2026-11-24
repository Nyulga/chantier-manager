# Journal du lot S6 – Sécuriser la démo

**Issue** : #45 · **Statut** : en cours depuis le 2026-11-24 · **Plage** : `ee4b35a..`

Le lot fait suite au premier test d'intrusion local (règle 08) et à la demande du propriétaire de protéger la démo publique, où l'écriture est ouverte à tous. Le plan a été validé par le propriétaire le 2026-11-24.

## Décisions du propriétaire

- **Limites de débit** : 20 écritures et 120 lectures par minute et par adresse ; une adresse qui touche un piège est bloquée en écriture pendant 1 heure.
- **Plafonds de volume** : 100 chantiers en tout, 30 étapes par chantier. La démo n'est **pas** remise à zéro : une fois le plafond atteint, plus aucune création n'est possible, et le propriétaire décidera de la suite.
- **Mise en ligne** : étape séparée, après le lot, avec accord pour chaque commande sur le serveur (le bloc Caddy du serveur change).
- **Hors lot** : fail2ban sur le serveur (lot 08) ; le code d'erreur d'un ouvrier qui tente de valider (issue à part).

## Étape 1 – Domaine et services (`dev-metier`, Opus, effort élevé)

**Textes propres (constat M4)** : nouvelle garde `app/shared/domain/caracteres.py`, appliquée à chaque champ texte. Sont refusés les caractères de contrôle (`Cc`), les demi-codets isolés (`Cs`) et les caractères bidirectionnels (U+202A–U+202E, U+2066–U+2069, risque d'usurpation d'affichage). Champs sur une ligne (nom, client, voie, code postal, ville, titre d'étape) : aucun contrôle admis. Commentaire d'une transition : `\n`, `\r` et `\t` admis. Le message d'erreur est fixe et désigne le champ (ADR 0008).

**Plafonds** : `LIMITE_CHANTIERS = 100`, `LIMITE_ETAPES_PAR_CHANTIER = 30`, nouvelle `PlafondAtteintError` (`shared/application/erreurs.py`). Le droit est vérifié d'abord, puis le plafond, dans la transaction et avant toute écriture.

**Découpage des couches** : une première version ajoutait un comptage au port et à l'infrastructure ; le propriétaire l'a refusé (pas d'entorse au découpage). Le comptage s'appuie sur les lectures existantes (`lister()`, et la lecture des étapes déjà faite pour l'ordre), bornées par ces mêmes plafonds. Infrastructure et tests de contrat intacts (`git diff --stat` vide). Le besoin d'un garde-fou automatique est suivi dans l'issue #46.

**Donnée de test corrigée** : `tests/integration/etapes/test_api_tableau_de_bord.py` créait 51 étapes sur un seul chantier ; elle les répartit désormais sur plusieurs chantiers.

**Rouge** : textes `115 failed, 10 passed` (`Failed: DID NOT RAISE ValeurInvalideError`) ; plafonds `4 failed, 10 passed` (`DID NOT RAISE PlafondAtteintError`).
**Vert** (`just verifier`, coordinateur) : `797 passed`, couverture backend 100 %, domain et application `687 0 48 0 100%`, 8 contrats tenus, `458` tests frontend.

**Reste pour l'étape 3 (`dev-api`)** : `PlafondAtteintError` → 409, tests d'intégration du 409 et du 422 sur un caractère nul.
