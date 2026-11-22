---
paths:
  - "backend/app/*/domain/**"
---

# Règle 01 – Couche `domain` (le cœur métier)

Relire d'abord `00-principes.md`.

## Rôle
Porter **toutes** les règles métier : les invariants, la machine à états des étapes, le calcul de l'avancement, les politiques d'accès et les erreurs métier. C'est la seule couche qui *décide*.

## Autorisé
- La bibliothèque standard Python uniquement : `dataclasses`, `enum`, `decimal`, `datetime` (types seulement), `uuid` (le type `UUID` seulement), `typing`.
- Les imports depuis le `domain` du même module, ou depuis `app.shared.domain`.

## Interdit
- Tout import de FastAPI, Pydantic, SQLAlchemy, Alembic, psycopg, structlog, et de toute bibliothèque tierce.
- Tout import d'`application`, d'`infrastructure` ou d'`api`, et du `domain` d'un **autre** module métier.
- Toute entrée-sortie : base de données, fichiers, réseau, logs, variables d'environnement, `print`.
- Toute source non déterministe : `datetime.now()`, `uuid7()`, `random`. **L'heure et les identifiants sont reçus en paramètres** ; l'application les obtient des ports `Horloge` et `GenerateurId`.
- Les types `float` pour l'argent. `Montant` repose sur `Decimal`.

## Patterns obligatoires
| Pattern | Application |
|---|---|
| **Entity** | `@dataclass` (**sans `slots` et non figée** : le mapping impératif de SQLAlchemy doit pouvoir y attacher son état, voir l'ADR 0002 ; décision du 2026-11-22) avec une identité (`id: UUID`), et des **méthodes métier** qui modifient l'état (`etape.signaler_terminee(acteur, maintenant)`). Pas de *setters* publics « nus ». |
| **Value Object** | `@dataclass(frozen=True, slots=True)`, validé dans `__post_init__`. Il est persisté via `composite()`, jamais mappé comme une table : `Adresse`, `Montant`, `Email`, `Commentaire`. Une valeur invalide **ne peut pas exister**. |
| **Aggregate** | `Chantier` est une racine : ses affectations ne se modifient que par ses méthodes. On ne référence un autre agrégat que **par son identifiant**. |
| **State** | Le cycle d'une étape est une **table de transitions déclarative** (statut de départ × action × rôle → statut d'arrivée). Une transition absente de la table lève `TransitionInterdite`. Chaque transition produit une entrée `HistoriqueEtape`. |
| **Specification / Policy** | Des fonctions pures `peut_voir(...)`, `peut_modifier(...)`, `peut_valider(...)`… qui renvoient `bool` et ne lèvent rien. |
| **Factory** | Une méthode de classe `creer(...)` pour chaque entité, qui garantit qu'un objet naît toujours valide. |
| **Erreurs métier** | Une hiérarchie de classes qui héritent de `ErreurMetierError` (`app.shared.domain`) : `TransitionInterditeError`, `AccesRefuseError`, `NonTrouveError`, `ValeurInvalideError`… Le suffixe `Error` est imposé par la règle ruff `N818` (décision du 2026-11-22). Dans les documents, on garde le nom court : `NonTrouve` désigne `NonTrouveError`. Le message est en français et ne contient aucune donnée personnelle. |

## Organisation des fichiers
- Un fichier par entité ou par objet valeur important : `chantier.py`, `adresse.py`, `montant.py`.
- `politiques.py` pour les politiques d'accès, `erreurs.py` pour les erreurs du module.
- Aucun fichier `models.py` ou `utils.py` fourre-tout.

## Tests (voir aussi `07-tests-et-migrations.md`)
- **TDD strict** : le test existe et échoue avant le code.
- **100 %** de couverture des lignes et des branches, et un score de mutation **≥ 90 %**.
- **hypothesis** sur la machine à états : aucune suite d'actions ne doit mener à un état non prévu.
- Une **matrice exhaustive** rôle × action × affectation teste les politiques d'accès : chaque cellule est un cas de test paramétré.
- Les tests n'utilisent ni base de données, ni mock : uniquement des objets du domaine.
