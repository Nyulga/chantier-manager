---
paths:
  - "backend/app/*/infrastructure/**"
---

# Règle 03 – Couche `infrastructure` (données et services externes)

Relire d'abord `00-principes.md`.

## Rôle
Implémenter les ports déclarés par `application`. **C'est la seule couche qui parle à la base de données**, au disque, à ClamAV, au serveur SMTP, ou à toute bibliothèque technique (Argon2, Pillow, JWT…).

## Autorisé
- L'`application` et le `domain` du même module, et `app.shared.*`.
- SQLAlchemy, psycopg (non installé pendant le squelette, ADR 0007), Pillow, pillow-heif, filetype, argon2-cffi, PyJWT, le client clamd, smtplib, structlog.

## Interdit
- Tout import d'`api` ou de FastAPI.
- Tout import de l'`infrastructure` d'un **autre** module.
- **Toute logique métier.** Un repository enregistre et recharge ; il ne décide rien.
- Un `commit` ou un `rollback` dans un repository : c'est le rôle exclusif de l'Unit of Work.
- Du SQL construit par concaténation de chaînes. Les requêtes passent par SQLAlchemy, avec des paramètres liés.
- Laisser fuir une exception technique (`sqlalchemy.exc.*`, `ConnectionError`, `OSError`…). Elle est **traduite** en erreur de l'application (`AntivirusIndisponible`, `StockageIndisponible`…), ou en erreur du domaine (`NonTrouve`).
- Logger une donnée personnelle, un mot de passe, un token ou le contenu d'un fichier.

## Patterns obligatoires
| Pattern | Application |
|---|---|
| **Adapter** | Une classe par implémentation de port, nommée d'après sa technologie : `SqlChantierRepository`, `ClamdScanneurAntivirus`, `SmtpEnvoiEmail`, `DisqueStockageFichiers`, `Argon2HacheurMotDePasse`. |
| **Data Mapper** | Le mapping impératif SQLAlchemy (`registry.map_imperatively`), écrit dans un seul fichier, `tables.py`, par module. Les entités du domaine restent des dataclasses pures : **aucune classe ORM en double**. |
| **Fake (In-memory)** | Pour chaque port, une implémentation mémoire (`MemoireChantierRepository`…), placée dans `infrastructure/memoire/`. Elle est utilisée par les tests de l'application. |
| **Anti-Corruption Layer** | Lot futur : l'adaptateur du prestataire de facturation convertit son modèle vers le nôtre. Aucun type externe ne traverse le port. |

## Robustesse et sécurité
- Tout appel réseau (ClamAV, SMTP) a un **délai d'attente explicite**.
- ClamAV injoignable : l'erreur est levée et **l'envoi est refusé** (fail closed). Il n'y a jamais d'acceptation par défaut.
- Les fichiers sont écrits hors du dossier public, sous un nom aléatoire, de façon atomique (fichier temporaire, puis renommage).
- Requêtes de liste : chargement explicite des relations nécessaires (pas de requêtes N+1) et pagination.

## Tests (voir aussi `07-tests-et-migrations.md`)
- **Tests de contrat** : une suite de tests unique par port, exécutée sur l'implémentation SQL (PostgreSQL réel via testcontainers ; SQLite pendant le squelette, voir l'ADR 0007) **et** sur l'implémentation mémoire. Les deux doivent se comporter exactement de la même façon (principe L).
- Les adaptateurs externes (ClamAV, SMTP) sont testés en intégration contre les conteneurs de développement : fichier EICAR pour ClamAV, Mailpit pour le SMTP.
