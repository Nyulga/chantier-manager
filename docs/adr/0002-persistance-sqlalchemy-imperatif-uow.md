# ADR 0002 : persistance avec SQLAlchemy synchrone, mapping impératif et Unit of Work

- **Statut** : accepté
- **Date** : 2026-11-22

## Contexte

Le domaine doit rester indépendant de l'ORM ([ADR 0001](0001-monolithe-modulaire-hexagonal.md)). On veut éviter d'avoir trois représentations par objet (entité du domaine, modèle ORM, schéma API) et tout le code de conversion qui va avec.

Certaines opérations doivent être atomiques :
- une transition d'étape et son historique ;
- l'enregistrement d'un fichier et de sa ligne en base ;
- la rotation d'un refresh token.

## Décision

- **PostgreSQL 16+** (pendant le squelette, SQLite : voir l'ADR 0007), avec **SQLAlchemy 2 en mode synchrone** et le pilote **psycopg 3**.
- **Mapping impératif** :
  - les entités du domaine sont des dataclasses ;
  - le mapping vers les tables est déclaré dans la partie `infrastructure` de chaque module ;
  - le domaine n'importe jamais SQLAlchemy.
- **Repositories** : une interface par agrégat dans `application`, avec deux implémentations, l'une SQL et l'autre en mémoire.
- **Unit of Work** : interface dans `shared/application`, avec une implémentation SQL et une implémentation mémoire.
  - Chaque cas d'usage s'exécute dans **un** UoW, avec un commit explicite.
  - Pour les fichiers : écriture du fichier, puis commit en base. Si le commit échoue, le fichier est supprimé (compensation).
- **Identifiants** : UUID v7, générés par le port `GenerateurId`.
- **Montants** : objet valeur `Montant`, basé sur `Decimal` (EUR), stocké en `NUMERIC(12,2)`.
- **Alembic** pour toutes les évolutions du schéma ; la cohérence avec les métadonnées est vérifiée en CI.

## Alternatives écartées

| Option | Raison du rejet |
|---|---|
| **SQLAlchemy async** | Complique le chargement des relations (*lazy loading*) et les tests, sans gain réel à cette charge. FastAPI exécute de toute façon les routes synchrones dans un pool de threads. |
| **Modèles ORM déclaratifs séparés + conversion manuelle** | Fait une troisième représentation et beaucoup de code de conversion à maintenir. |
| **Modèles déclaratifs utilisés comme domaine** | Couple le métier à l'ORM, contraire à l'ADR 0001. |
| **SQLModel** | Fusionne les modèles ORM et les schémas API, ce qui couple trois préoccupations distinctes. |
| **SQLite au départ** | Impose une migration de moteur plus tard, alors que PostgreSQL est aussi simple à lancer en conteneur. |

## Conséquences

- Le mapping impératif instrumente les dataclasses à l'exécution. Les tests du domaine ne chargent donc jamais ce mapping, pour rester purs.
- Le chargement des relations doit être explicite dans les repositories, pour éviter les requêtes N+1.
- Changer de moteur relationnel ne concerne que l'infrastructure. Changer pour un autre paradigme de stockage ne concerne que les repositories.
