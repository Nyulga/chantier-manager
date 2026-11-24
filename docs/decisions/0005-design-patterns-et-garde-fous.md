# ADR 0005 – Design patterns, principes SOLID et garde-fous contre le code spaghetti

- **Statut** : accepté
- **Date** : 2026-11-22

## Contexte
Le propriétaire du projet exige le respect strict des principes SOLID et de design patterns reconnus. Il refuse tout fichier fourre-tout et tout code spaghetti, et en fait une condition rédhibitoire.

Une architecture décrite seulement dans des documents se dégrade avec le temps. Il faut donc :
- des règles écrites, consultées avant chaque développement ;
- des garde-fous **automatiques**, qui font échouer la CI.

## Décision

### 1. Des règles par couche, dans `.claude/rules/`
- `00-principes.md` s'applique toujours : SOLID, limites chiffrées, nommage, TDD.
- `01` à `05` couvrent chacune une couche : `domain`, `application`, `infrastructure`, `api`, frontend.
- `06` couvre la composition root et le module `shared` ; `07` couvre les tests et les migrations.
- Chaque règle déclare les fichiers qu'elle concerne : Claude Code la charge automatiquement dès qu'il travaille sur ces fichiers.

### 2. Les patterns retenus
| Couche | Patterns |
|---|---|
| `domain` | Entity, Value Object, Aggregate, State (table de transitions), Specification/Policy, Factory, erreurs métier typées |
| `application` | Use Case (Command), Port (inversion des dépendances), Repository, Unit of Work, Chain of Responsibility (contrôle des fichiers), vue en lecture seule qui porte les actions permises |
| `infrastructure` | Adapter, Data Mapper (mapping impératif), Fake en mémoire, Anti-Corruption Layer (future facturation) |
| `api` | DTO, Mapper, traduction centralisée des exceptions, Middleware, Dependency Injection |
| Composition root | Dependency Injection, à un seul endroit |
| Frontend | Feature modules, hooks de service, Presentational/Container, Provider, Adapter autour du client généré |

### 3. Les anti-patterns interdits
Singleton et état global, Service Locator, Active Record, modèle anémique, god object, et tout pattern ajouté sans besoin réel.

### 4. Le frontend découpé en sous-couches
Le frontend suit un sens d'appel unique : `pages` → `services` → `api`. Seul `src/ui` (le design system Balise) produit du HTML stylé ; les pages et les composants des fonctionnalités n'assemblent que des composants `ui`.

Pour que le frontend n'ait jamais à recalculer une règle, les **actions permises** sont calculées par le backend et renvoyées dans les réponses.

### 5. Des garde-fous automatiques, configurés au lot 01
| Garde-fou | Outil |
|---|---|
| Sens des dépendances entre couches et entre modules (backend) | import-linter (contrats de couches, d'indépendance et d'interdiction : seule l'`infrastructure` peut importer SQLAlchemy ou psycopg) |
| Sens des dépendances (frontend) | ESLint : `eslint-plugin-boundaries`, `no-restricted-imports`, `import/no-cycle` |
| Design system obligatoire | ESLint : `react/forbid-elements` et `react/forbid-dom-props` hors de `src/ui`, valeurs Tailwind arbitraires interdites |
| Complexité et longueur | ruff (`C901`, `PLR0911`, `PLR0912`, `PLR0913`, `PLR0915`, `PLR2004`), ESLint (`complexity`, `max-lines`, `max-lines-per-function`, `max-depth`, `max-params`), et un script qui vérifie les limites de lignes par fichier et par fonction côté Python |
| Duplication | jscpd, ≤ 2 % |
| Désactivation de règles | Interdite, signalée par la revue et par un contrôle en CI (`noqa`, `type: ignore`, `eslint-disable`, `pragma: no cover`) |

## Alternatives écartées
- **Des règles seulement dans `CLAUDE.md`** : le fichier deviendrait trop long, et ces règles ne seraient pas ciblées sur la couche en cours de travail.
- **Des règles sans outillage** : sans échec en CI, elles ne seraient pas respectées dans la durée.
- **wemake-python-styleguide** : très complet, mais redondant avec ruff et en conflit avec certaines de ses règles. ruff, complété par un petit script de mesure des tailles, suffit.
- **Un store global côté frontend (Redux, Zustand)** : inutile, puisque l'état serveur est géré par TanStack Query.

## Conséquences
- Le lot 01 doit configurer **tous** ces garde-fous, et prouver qu'ils échouent sur une violation volontaire.
- Il y a un peu plus de fichiers, petits et nombreux. C'est voulu.
- Tout nouveau composant visuel passe d'abord par `src/ui`.
- Changer une limite ou un pattern nécessite un nouvel ADR.
