# ADR 0007 – SQLite pendant le squelette

- **Statut** : accepté. Il remplace en partie l'ADR 0002, pendant le squelette uniquement.
- **Date** : 2026-11-22 (lots S1 à S4)

## Contexte
L'ADR 0002 retient PostgreSQL et écarte « SQLite au départ ». Les règles 03 et 07 imposent des tests de contrat, d'intégration et de migration sur un vrai PostgreSQL, via testcontainers.

Pour livrer le squelette en ligne le soir même, le propriétaire a décidé de partir sur **SQLite**, en ligne compris (`docs/plan/squelette.md`, « Base de données »).

## Décision
Pendant le squelette :
- La base est **SQLite**, un fichier dans le volume Docker `chantier-donnees`.
- Le code ne change pas de nature : SQLAlchemy 2 synchrone, mapping impératif, Unit of Work et migrations Alembic. Seule l'URL de connexion (`CHANTIER_URL_BASE`) désigne SQLite.
- Les tests de contrat, d'intégration et de migration tournent sur **SQLite**. Les exigences « PostgreSQL réel via testcontainers » des règles 03 et 07 s'appliquent à partir de la phase 2.
- `historique_etapes.id` est un entier auto-incrémenté. Il n'est jamais exposé par l'API, et sert seulement à départager deux entrées de même date. Les identifiants exposés restent des UUID v7.

## Conséquences
- **Passage à PostgreSQL en phase 2** :
  - changer l'URL de connexion ;
  - ajouter le conteneur PostgreSQL ;
  - jouer les suites de contrat et de migration sur PostgreSQL (#30) ;
  - reprendre les données de la démo, ou repartir d'une base vide.
- **Points à revérifier à ce moment-là** : l'ordre `NULLS FIRST`, le tri des UUID et des dates avec fuseau, et les types `Numeric`. Ils sont écrits de façon portable, mais testés seulement sur SQLite.
- **Limite connue** : SQLite n'accepte qu'un seul écrivain à la fois. L'API tourne avec un seul worker, ce qui suffit pour une démonstration.
