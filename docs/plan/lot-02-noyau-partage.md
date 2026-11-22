# Lot 02 – Noyau partagé

**Dépend de** : 01 · **Statut** : à faire

## Objectif
Fournir au module `shared` les briques techniques communes, avec leurs ports, leurs implémentations SQL et leurs implémentations mémoire, pour que les lots métier n'aient plus qu'à s'y brancher.

## Contenu
- **Configuration** : pydantic-settings, validation au démarrage (l'application refuse de démarrer si la configuration est invalide), séparation des secrets.
- **Base de données** : moteur SQLAlchemy synchrone (psycopg 3), registre de mapping impératif, gestion des sessions.
- **Unit of Work** : port `UnitOfWork`, avec les implémentations `SqlUnitOfWork` et `InMemoryUnitOfWork`, et des tests communs exécutés sur les deux.
- **Alembic** : configuration, migration initiale (vide), et vérification en CI que le schéma correspond aux métadonnées.
- **Ports transverses** : `Horloge` (système et fixe), `GenerateurId` (UUID v7 et déterministe pour les tests).
- **Erreurs** : hiérarchie d'erreurs du domaine, traduites en réponses HTTP (format de problème RFC 9457) dans un seul gestionnaire.
- **Sécurité HTTP** : middleware d'en-têtes (CSP, HSTS, nosniff, Referrer-Policy, Permissions-Policy), protection CSRF en *double submit*, limite de taille des requêtes.
- **Logs** : structlog en JSON, identifiant de requête, et filtrage des données sensibles.
- **Composition root** : `app/main.py` assemble les dépendances via le `Depends` de FastAPI.
- **Tests d'intégration** : fixture testcontainers PostgreSQL, et client HTTP de test.

## Critères d'acceptation
- [ ] Une transaction annulée dans le UoW SQL ne laisse aucune trace en base, et le UoW mémoire se comporte de la même façon (tests communs).
- [ ] Les en-têtes de sécurité sont présents sur toutes les réponses (test d'intégration).
- [ ] Une requête qui modifie des données sans token CSRF valide est rejetée (403).
- [ ] Une erreur du domaine produit la bonne réponse HTTP, sans fuite de trace interne.
- [ ] Les logs ne contiennent ni mot de passe, ni token, ni cookie (test).

## Hors lot
Toute entité métier.
