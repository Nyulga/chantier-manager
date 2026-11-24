---
paths:
  - "backend/tests/**"
  - "backend/migrations/**"
  - "frontend/**/*.test.ts"
  - "frontend/**/*.test.tsx"
  - "frontend/e2e/**"
---

# Règle 07 – Tests et migrations

Relire d'abord `00-principes.md`.

**Pourquoi une règle dédiée** : des tests faibles donnent une couverture de 100 % qui ne prouve rien, et une migration mal écrite peut détruire des données en production. Les deux méritent des règles aussi strictes que le code.

## Tests

### Organisation (backend)
```
backend/tests/
├── domain/<module>/           # tests du code de app/<module>/domain, sans base ni réseau
├── application/<module>/      # cas d'usage et services publics, sur des fakes mémoire
├── infrastructure/<module>/   # tests unitaires de l'infrastructure : types SQL, UoW, implémentations mémoire, horloge réelle
├── api/<module>/              # tests de la couche api qui ne passent pas par HTTP (par exemple la parité des schémas)
├── composition/               # tests de la composition root
├── outils/                    # tests des outils du dossier tools
├── fabriques/<module>.py      # fabriques de données fictives servant à plusieurs couches
├── contrats/                  # une suite par port, jouée sur SQL ET mémoire
├── integration/<module>/      # routes API + PostgreSQL réel (testcontainers ; SQLite pendant le squelette, ADR 0007)
├── migrations/                # application, annulation et réapplication des migrations
└── architecture/              # contrats import-linter et limites de taille
```
Un fichier de test va dans le dossier de la couche **du code qu'il teste**. S'il en exerce plusieurs, on choisit la couche la plus haute. Une aide de test (espion, contexte) reste à côté des tests qui l'utilisent ; une fabrique utilisée par plusieurs couches va dans `fabriques/`.

Côté frontend : un fichier `*.test.tsx` à côté du fichier testé, et les tests Playwright dans `frontend/e2e/`.

### Règles d'écriture
- **TDD** : le test est écrit et vu en échec **avant** le code métier qu'il couvre.
- **Un test = un comportement.** Le nom le décrit en français : `test_ouvrier_ne_peut_pas_valider_une_etape`.
- Structure **Arrange / Act / Assert**, séparée par une ligne vide. Pas de logique (`if`, boucle) dans un test ; on utilise la paramétrisation.
- **Doubles de test** : les implémentations **mémoire** des ports (des fakes), jamais `unittest.mock` sur notre propre code. Un mock n'est toléré qu'à la frontière d'une bibliothèque externe impossible à lancer, et seulement avec l'accord de l'utilisateur.
- Les tests sont **déterministes** : horloge fixe (`HorlogeFixe`), identifiants prévisibles, aucun `sleep`, aucun accès à Internet.
- Les tests sont **indépendants** : chacun prépare ses propres données. L'ordre d'exécution n'a aucune importance.
- Les données de test sont **fictives** (aucune donnée réelle de client ou de chantier). On utilise des fabriques de test (`un_chantier(...)`), pas des fixtures géantes partagées.
- Ce qu'on vérifie : un résultat ou un état observable, jamais un détail d'implémentation.
- Interdit de supprimer, d'ignorer (`skip`, `xfail`) ou d'affaiblir un test pour faire passer la CI.

### Seuils (bloquants en CI)
- Domaine et services : 100 % des lignes et des branches, et un score de mutation ≥ 90 %.
- Backend global : ≥ 95 % des lignes et des branches. Frontend : ≥ 90 %.
- Exclure du code de la mesure de couverture (`pragma: no cover`) est interdit, sauf accord de l'utilisateur.

### Tests obligatoires par type de code
| Code | Tests |
|---|---|
| Machine à états | Tableau exhaustif des transitions, plus hypothesis (propriétés : aucun état invalide accessible, historique toujours complet) |
| Politiques d'accès | Matrice rôle × action × affectation, une cellule par cas |
| Cas d'usage | Cas nominal, chaque refus de droit, chaque erreur métier, annulation de la transaction |
| Port | Suite de contrat jouée sur chaque implémentation |
| Route | Nominal, 401, 403, 404, 409 ou 422 selon le cas |
| Parcours utilisateur | Playwright : chef (créer un chantier, définir les étapes, valider, refuser) et ouvrier (signaler, envoyer une photo), à 360 px et 1280 px |

## Migrations (Alembic)

- **Toute** modification du schéma passe par une migration Alembic. On ne modifie jamais la base à la main.
- Une migration générée automatiquement (`--autogenerate`) est **relue et corrigée** avant d'être commitée.
- Une migration = un changement cohérent, avec un nom explicite : `ajoute_table_etapes`.
- `upgrade` **et** `downgrade` sont écrits et testés : un test applique toutes les migrations, puis les annule, puis les réapplique, sur un PostgreSQL réel (SQLite pendant le squelette, ADR 0007).
- **Aucune perte de données** :
  - pour renommer une colonne ou changer son type, on procède en plusieurs étapes (ajout, copie, suppression), jamais par une suppression directe ;
  - toute suppression de données est signalée à l'utilisateur avant d'être écrite.
- On ne modifie **jamais** une migration déjà poussée sur `dev` : on en ajoute une nouvelle.
- Contraintes en base en plus du domaine (défense en profondeur) : `NOT NULL`, clés étrangères, `CHECK` sur les montants positifs et les statuts, index sur les clés de recherche.
- Un test vérifie que le schéma issu des migrations correspond aux tables déclarées (`alembic check`).
