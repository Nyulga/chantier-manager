---
paths:
  - "backend/app/*/api/**"
---

# Règle 04 – Couche `api` (présentation HTTP)

Relire d'abord `00-principes.md`.

## Rôle
Traduire une requête HTTP en appel d'un cas d'usage, puis traduire le résultat en réponse HTTP. **Rien de plus.**

## Autorisé
- La couche `application` du même module : ses cas d'usage, ses commandes et ses vues.
- `application/valeurs_publiques.py` du même module : les seules constantes de saisie (bornes) et les types de valeur immuables (`Role`) que le domaine republie pour les schémas. Ce fichier ne contient jamais d'entité, de règle ni de fonction (ADR 0008).
- `app.shared.api` (gestion des erreurs, dépendances d'authentification, sécurité).
- FastAPI et Pydantic.

## Interdit
- Tout import de `domain` (sauf les erreurs, et seulement dans le traducteur central d'erreurs de `shared`) et tout import d'`infrastructure`.
- Toute utilisation directe de la session SQLAlchemy, de l'Unit of Work ou d'un repository.
- **Toute logique métier ou de droits** : pas de `if utilisateur.role == ...` dans une route.
- Un `try/except` dans une route : les erreurs sont traduites par le gestionnaire central.
- Renvoyer une entité du domaine ou un dictionnaire libre : on renvoie toujours un schéma de réponse déclaré.
- Instancier une implémentation : les cas d'usage arrivent par `Depends`, fournis par la composition root.

## Patterns obligatoires
| Pattern | Application |
|---|---|
| **DTO** | Des schémas Pydantic distincts pour l'entrée (`CreerChantierRequete`) et la sortie (`ChantierReponse`), avec `model_config = ConfigDict(extra="forbid", frozen=True)`. Ils sont rangés dans `schemas.py`. |
| **Mapper** | Une fonction explicite par conversion, rangée dans `conversions.py` : requête → commande, vue → réponse. Pas de conversion implicite. |
| **Exception Translation** | Un seul gestionnaire, dans `app.shared.api` : `NonTrouve` → 404, `AccesRefuse` → 403, `TransitionInterdite` → 409, `ValeurInvalide` → 422, indisponibilités techniques → 503. Les corps d'erreur ont un format unique, un message en français, et aucun détail interne. |
| **Middleware** | En-têtes de sécurité, vérification CSRF et identifiant de requête, dans `app.shared.api`. Ils ne sont jamais réimplémentés dans une route. **Pendant le squelette**, il n'y en a pas encore : les en-têtes de sécurité et la limite de taille sont posés par Caddy (ADR 0015), et le CSRF arrivera au lot 03 avec les cookies de session. |
| **Dependency Injection** | `Depends` pour obtenir l'acteur authentifié et le cas d'usage. |

## Contrat d'erreur (ADR 0008)
- **Toute** erreur, y compris un 404 de route, un 405 ou un identifiant mal formé, répond en `application/problem+json` (RFC 9457) : `{type, title, status, detail}`, schéma `ProblemeReponse`.
- **422** : il ajoute `erreurs: [{champ, message}]`. `champ` est un chemin pointé du corps (`adresse.code_postal`) ou un paramètre. Les messages sont fixes et ne recopient **jamais** la saisie.
- **409** : transition interdite, version périmée (`ConflitVersionError`) ou ajout simultané.
- **503** : réservé aux vraies indisponibilités de la base (verrou, fichier inaccessible, disque plein, connexion perdue). Une erreur de programmation reste une 500. La cause est journalisée, sans paramètres SQL.
- **Liste plafonnée** : l'en-tête `X-Liste-Tronquee: true` annonce qu'il reste des éléments.
- Les statuts et actions restent des `Literal` dans les schémas ; un test de parité les compare aux énumérations du domaine.

## Forme d'une route
Une route fait au plus 15 lignes. Elle se lit toujours dans le même ordre :
1. recevoir le DTO validé et l'acteur ;
2. le convertir en commande ;
3. appeler `cas_usage.executer(commande, acteur)` ;
4. convertir la vue en réponse et la renvoyer.

Elle déclare aussi :
- `response_model` et `status_code`, explicites ;
- des `responses` documentées pour les erreurs (OpenAPI), car le client frontend est généré à partir de ce schéma.

## Organisation
- Un fichier `routes.py` par module (ou un fichier par ressource si le module grossit), plus `schemas.py` et `conversions.py`.
- Les URL sont en français, au pluriel, sans verbe sauf pour les actions métier : `/api/chantiers/{id}/etapes/{id}/valider`.

## Tests (voir aussi `07-tests-et-migrations.md`)
- Chaque route a des tests d'intégration (httpx, avec un vrai PostgreSQL ; SQLite pendant le squelette, ADR 0007) qui couvrent :
  - le cas nominal ;
  - 401 (non connecté), à partir du lot 03 ;
  - 403 (connecté, mais action interdite) ;
  - 404 (hors périmètre) ;
  - 409 et 422 quand ils s'appliquent ;
  - l'absence du budget dans les réponses destinées à un ouvrier.

## Comment vérifier
- **Automatique** (`just verifier`) :
  - import-linter : « L'api d'un module métier n'importe pas le domaine », « Couches de chaque module » ;
  - tests dans `backend/tests/integration/` (forme des erreurs, 422 par champ, 503, en-têtes) et `backend/tests/api/` (parité des `Literal`) ;
  - le schéma OpenAPI est exporté par `just client` ; `tsc` échoue côté frontend si une route ou un champ change sans régénération.
- **Par un agent** : `conformite` (route de 15 lignes au plus, pas de `try/except`, DTO en `extra="forbid"`, conversions explicites), `pentest` (forme réelle des erreurs, méthodes, taille, en-têtes).
- **Pas encore vérifié** : la longueur des routes et `extra="forbid"` n'ont pas de contrôle automatique ; la CI ne vérifie pas encore que le client généré est à jour (issue #43).
