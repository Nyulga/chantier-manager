# Lot 02 – Noyau partagé

**Dépend de** : 01 · **Statut** : à faire · **Issue** : #2 · **Références** : [ADR 0002](../adr/0002-persistance-sqlalchemy-imperatif-uow.md), règle [06](../../.claude/rules/06-composition-et-shared.md)

## Objectif
Fournir au module `shared` les briques techniques communes, avec leurs ports, leurs implémentations SQL et leurs implémentations mémoire, pour que les lots métier n'aient plus qu'à s'y brancher.

## Prérequis et points à trancher au démarrage
- Aucun.

## Étapes
| # | Agent (modèle, effort) | Contenu | Règles |
|---|---|---|---|
| 1 | `dev-metier` (Opus, élevé) | `shared/domain` : `ErreurMetier` et ses sous-classes communes (`NonTrouve`, `AccesRefuse`, `TransitionInterdite`, `ConflitDeModification`, `ValeurInvalide`), `Acteur` (identifiant et rôle), `Role`. `shared/application` : ports `UnitOfWork`, `Horloge`, `GenerateurId` et **`JournalAudit`**. Ce dernier enregistre les actions sensibles (type d'action, acteur, cible, date), sans aucune donnée sensible ; il sert dès le lot 03. Fakes `MemoireUnitOfWork`, `HorlogeFixe`, `GenerateurIdPrevisible` et `MemoireJournalAudit`. | 00, 01, 02, 06 |
| 2 | `dev-donnees` (Sonnet, élevé) | `Parametres` (pydantic-settings) : l'application refuse de démarrer si la configuration est invalide. Moteur SQLAlchemy synchrone (psycopg 3), registre de mapping impératif, `SqlUnitOfWork`. **Suite de contrat** `UnitOfWork`, jouée sur la version SQL et sur la version mémoire. `HorlogeSysteme`, `GenerateurUuid7`. Alembic : configuration et migration initiale, `alembic check` en CI. Fixture testcontainers PostgreSQL. structlog en JSON, avec un filtre des données sensibles. | 00, 03, 06, 07 |
| 3 | `dev-api` (Sonnet, moyen) | `shared/api` : gestionnaire central des erreurs, au format de problème RFC 9457 et avec un message en français, sans détail interne. Middlewares : en-têtes de sécurité (CSP, HSTS, nosniff, Referrer-Policy, Permissions-Policy), CSRF en *double submit*, identifiant de requête, limite de taille des requêtes. Composition root : `app/main.py` (l'application, les routeurs, les middlewares) et `app/composition/shared.py` (les fournisseurs). | 00, 04, 06 |
| 4 | `dev-frontend` (Sonnet, élevé) | `src/api/client.ts` : seul adaptateur du client généré. Il gère la base `/api`, l'envoi des cookies et de l'en-tête CSRF, et lit les erreurs au format RFC 9457. Composant `Alerte` pour afficher une erreur. | 00, 05 |

## Composants `ui` introduits
`Alerte` (types : information, erreur, succès).

## Critères d'acceptation → tests
| Critère | Test qui le prouve | Couche |
|---|---|---|
| Une transaction annulée dans le UoW SQL ne laisse aucune trace en base, et le UoW mémoire se comporte de la même façon | `tests/contrats/test_unit_of_work.py`, joué sur les deux implémentations | Données |
| `JournalAudit` mémoire enregistre et restitue les entrées dans l'ordre, sans champ sensible | `tests/unitaires/shared/test_journal_audit_memoire.py` | Service |
| Les en-têtes de sécurité sont présents sur toutes les réponses | `tests/integration/shared/test_entetes_securite.py` | API |
| Une requête qui modifie des données sans token CSRF valide est rejetée (403) | `tests/integration/shared/test_csrf.py` | API |
| Une requête plus volumineuse que la limite est rejetée (413) avant d'être lue en entier | `tests/integration/shared/test_limite_taille.py` | API |
| Une erreur du domaine produit le bon code HTTP au format RFC 9457, sans trace interne | `tests/integration/shared/test_traduction_erreurs.py` (paramétré, un cas par erreur) | API |
| Les logs ne contiennent ni mot de passe, ni token, ni cookie | `tests/unitaires/shared/test_filtre_logs.py` | Données |
| Une configuration invalide empêche le démarrage, avec un message clair | `tests/unitaires/shared/test_parametres.py` | Données |
| Le client frontend envoie l'en-tête CSRF et transforme une erreur RFC 9457 en message affichable | `src/api/client.test.ts` (MSW) | Frontend |

## Hors lot
Toute entité métier, et le stockage du journal d'audit en base (lot 07).
