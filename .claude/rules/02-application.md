---
paths:
  - "backend/app/*/application/**"
---

# Règle 02 – Couche `application` (la couche service)

Relire d'abord `00-principes.md`.

## Rôle
Exécuter les **cas d'usage**. Pour chaque cas d'usage, le service :
1. charge les objets nécessaires ;
2. **vérifie les droits** grâce aux politiques du domaine ;
3. demande au domaine d'appliquer la règle ;
4. enregistre le résultat dans **une seule transaction** ;
5. renvoie une vue en lecture seule.

**C'est la seule entrée vers le métier.** L'API et les tâches CLI n'appellent rien d'autre.

## Autorisé
- Le `domain` du même module, et `app.shared.domain` / `app.shared.application`.
- La couche `application` d'un **autre** module, uniquement via ses cas d'usage publics ou ses ports publics, exportés dans son `__init__.py`. Exemple : `etapes` utilise `chantiers.application.VerifierAffectation`.
- La bibliothèque standard, et `typing.Protocol` pour déclarer les ports.

## Interdit
- Tout import d'`infrastructure` ou d'`api`, de FastAPI, Pydantic, SQLAlchemy, psycopg ou de tout client externe.
- **Écrire une règle métier ici.** Une condition sur l'état d'un objet (« si le statut est… ») appartient au domaine. Le service *demande*, le domaine *décide*.
- Renvoyer une entité du domaine à l'appelant : on renvoie une **vue** (une dataclass figée).
- Lire la configuration ou l'environnement : les valeurs utiles sont injectées par la composition root.
- Attraper une `ErreurMetier` pour la masquer : elle remonte jusqu'à l'API, qui la traduit.

## Patterns obligatoires
| Pattern | Application |
|---|---|
| **Use Case (Command)** | Une classe par cas d'usage, dans son propre fichier (`signaler_etape_terminee.py`). Ses dépendances arrivent par le constructeur. Une seule méthode publique, `executer(commande, acteur)`. La commande est une `@dataclass(frozen=True)` (`SignalerEtapeTerminee`). |
| **Port** | Un `Protocol` par besoin, dans `ports.py` : `ChantierRepository`, `Horloge`, `StockageFichiers`, `ScanneurAntivirus`, `EnvoiEmail`… Il est **petit** et défini selon le besoin des cas d'usage (principe I). |
| **Repository** | Une interface par agrégat. Elle charge et enregistre des agrégats complets. Elle ne contient **jamais** de `commit`. |
| **Unit of Work** | `with self._uow:` englobe tout le cas d'usage. `self._uow.valider()` est appelée **une seule fois**, à la fin. Une exception provoque l'annulation complète. |
| **Chain of Responsibility** | La chaîne de contrôle des fichiers : chaque maillon (taille, format réel, antivirus, réencodage, stockage) est une classe qui implémente le même port `ControleFichier`. L'ordre est fixé dans la composition root. |
| **Vue (read model)** | `@dataclass(frozen=True)` renvoyée au lieu de l'entité. **Le service décide des champs visibles selon l'acteur** : le budget n'est présent dans la vue que si l'acteur est chef du chantier. Les **actions permises** (`peut_valider`, `peut_refuser`…) sont calculées ici, à partir des politiques, et incluses dans la vue. Le frontend n'a ainsi jamais à recalculer une règle. |

## Règles de sécurité
- **Chaque** cas d'usage vérifie les droits, même pour une simple lecture.
- Un chantier hors du périmètre de l'acteur lève `NonTrouve` (et non `AccesRefuse`), pour ne pas révéler son existence.
- L'acteur (`Acteur` : identifiant et rôle) est toujours un paramètre explicite, jamais une variable globale.

## Tests (voir aussi `07-tests-et-migrations.md`)
- **TDD strict**, avec **100 %** de couverture des lignes et des branches, et un score de mutation **≥ 90 %**.
- Les tests utilisent **uniquement les implémentations mémoire** des ports (repositories, UoW, horloge fixe, stockage, antivirus factice). Pas de `unittest.mock`.
- Chaque cas d'usage teste au minimum : le cas nominal ; chaque refus de droit ; chaque erreur métier ; l'annulation de la transaction en cas d'échec.
