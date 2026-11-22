# Règle 00 – Principes communs (toujours applicable)

Cette règle s'applique à **tout** le code du projet, dans chaque lot. Elle complète `intent.md`, qui reste la source de vérité. Les règles par couche (`01` à `07`) détaillent ce qu'elle impose.

## 1. Avant de coder (à chaque lot, à chaque tâche)

1. Relire `intent.md`, puis le fichier du lot dans `docs/plan/`.
2. Relire **cette règle** et la règle de **chaque couche** que la tâche va toucher.
3. Vérifier que la branche courante est `dev`.
4. Si une demande contredit une règle, **s'arrêter et le signaler à l'utilisateur**. Ne jamais contourner une règle en silence.

## 2. Les couches et leur unique responsabilité

| Couche | Rôle | Seule autorisée à… | Règle |
|---|---|---|---|
| `domain` | Règles métier pures | porter les invariants et les règles | `01-domain.md` |
| `application` | Cas d'usage (la « couche service ») | orchestrer, vérifier les droits, ouvrir une transaction | `02-application.md` |
| `infrastructure` | Accès aux données et services externes | **parler à la base**, au disque, à ClamAV, au SMTP | `03-infrastructure.md` |
| `api` | Présentation HTTP | traduire HTTP ↔ cas d'usage | `04-api.md` |
| Frontend | Présentation visuelle | afficher, avec **uniquement** les composants du design system | `05-frontend.md` |
| Composition root et `shared` | Assemblage et technique transverse | brancher les implémentations sur les ports | `06-composition-et-shared.md` |
| Tests et migrations | Preuves et évolutions du schéma | — | `07-tests-et-migrations.md` |

Chaînes d'appel autorisées, **et aucune autre** :
- Backend : `api` → `application` → `domain`. `infrastructure` implémente les ports d'`application`.
- Frontend : `pages` → `services` (hooks) → `api` (client généré) → backend. Les `pages` et `components` n'affichent que des composants de `ui`.

## 3. SOLID, traduit en règles vérifiables

| Principe | Ce que ça veut dire ici |
|---|---|
| **S** – Responsabilité unique | Un cas d'usage = une classe = un fichier. Un composant React = une seule chose à afficher. Un fichier qui fait « et aussi… » doit être découpé. |
| **O** – Ouvert/fermé | On étend en **ajoutant** (un nouvel adaptateur, un nouveau maillon dans la chaîne des fichiers, une ligne dans la table des transitions), pas en ajoutant des `if` dans du code existant. |
| **L** – Substitution de Liskov | Chaque port a au moins deux implémentations (SQL et mémoire), et **les deux passent la même suite de tests de contrat**. |
| **I** – Ségrégation des interfaces | Des ports petits et ciblés (`Protocol`), définis selon le besoin du cas d'usage. Pas de repository « fourre-tout » de vingt méthodes. |
| **D** – Inversion des dépendances | Le métier dépend d'interfaces, jamais d'implémentations. Les dépendances arrivent par le constructeur. Seule la composition root instancie les implémentations. Vérifié par import-linter. |

## 4. Zéro code spaghetti, zéro fichier fourre-tout : limites chiffrées

Ces limites sont **vérifiées automatiquement** (lint, pre-commit et CI, configurés au lot 01). Un dépassement fait échouer la CI.

| Mesure | Python | TypeScript |
|---|---|---|
| Lignes par fichier | ≤ 300 | ≤ 250 |
| Lignes par fonction | ≤ 40 | ≤ 60 (composants compris) |
| Complexité cyclomatique par fonction | ≤ 8 (ruff `C901`) | ≤ 8 (ESLint `complexity`) |
| Branches / `return` / instructions par fonction | ≤ 8 / ≤ 4 / ≤ 25 (ruff `PLR0912`, `PLR0911`, `PLR0915`) | — |
| Paramètres par fonction | ≤ 5 (ruff `PLR0913`) | ≤ 3 (ESLint `max-params`) ; un composant reçoit un seul objet `props` |
| Profondeur d'imbrication | ≤ 3 | ≤ 3 (ESLint `max-depth`, `max-nested-callbacks`) |
| Code dupliqué (jscpd) | ≤ 2 % | ≤ 2 % |
| Imports circulaires | interdits (import-linter) | interdits (`import/no-cycle`) |

En plus :
- **Pas de valeur magique** : les constantes métier ont un nom (`DUREE_INVITATION = timedelta(hours=72)`).
- **Retour anticipé** plutôt qu'imbrication de `if`.
- **Pas de code mort, pas de code commenté**, pas de `TODO` sans lot associé.
- **Pas de fichiers « utils », « helpers », « common » ou « misc »**. Un code transverse a un nom qui dit ce qu'il fait (`format_montant.ts`, `horloge.py`).
- **Désactiver une règle est interdit** (`# noqa`, `# type: ignore`, `eslint-disable`, `@ts-expect-error`, `cast`). Si c'est vraiment inévitable, s'arrêter et demander l'accord de l'utilisateur ; la justification est alors écrite sur la même ligne.

## 5. Design patterns

Les patterns imposés sont listés dans chaque règle de couche et justifiés dans [`docs/adr/0005-design-patterns-et-garde-fous.md`](../../docs/adr/0005-design-patterns-et-garde-fous.md).

**Anti-patterns interdits partout** :
- Singleton et état global mutable ;
- Service Locator ;
- Active Record ;
- modèle anémique (des règles métier écrites dans les services plutôt que dans le domaine) ;
- god object / god service ;
- pattern ajouté « au cas où », sans besoin réel dans le lot en cours.

## 6. Nommage

- Le **langage métier est en français**, partout : `Chantier`, `Etape`, `valider`, `SignalerEtapeTerminee`.
- Les identifiants n'ont **pas d'accents**. Les termes techniques des patterns restent en anglais : `Repository`, `UnitOfWork`, `Adapter`.
- Python : `snake_case` pour les fichiers, fonctions et variables ; `PascalCase` pour les classes.
- TypeScript : `PascalCase.tsx` pour les composants, `useQuelqueChose.ts` pour les hooks, `camelCase` pour le reste.
- Un nom dit **ce que fait** la chose, jamais comment elle est faite : `ChantierRepository`, et pas `ChantierDao`.

## 7. Méthode de travail : TDD obligatoire

Pour toute règle métier et tout cas d'usage, on suit le cycle **rouge → vert → refactorisation** :
1. écrire le test et **le voir échouer** ;
2. écrire le minimum de code pour le faire passer ;
3. refactoriser, avec les tests au vert.

Ordre de construction d'une fonctionnalité (tranche verticale) :
1. tests du domaine, puis domaine ;
2. tests des cas d'usage (avec les implémentations mémoire), puis cas d'usage ;
3. tests de contrat des ports, puis adaptateurs d'infrastructure, puis migration ;
4. tests d'API, puis routes ;
5. services frontend, puis composants `ui` manquants, puis pages ;
6. test de bout en bout (Playwright).

## 8. Fin de tâche

Avant de déclarer une tâche terminée :
- **Relecture** du code produit contre cette règle et contre la règle de chaque couche touchée.
- Lint, typage, contrats d'architecture et tests sont **tous verts en local**.
- La définition de « terminé » du lot (`docs/plan/README.md`) est respectée.
