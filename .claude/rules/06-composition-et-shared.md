---
paths:
  - "backend/app/main.py"
  - "backend/app/composition/**"
  - "backend/app/shared/**"
  - "backend/app/cli/**"
---

# Règle 06 – Composition root et module `shared`

Relire d'abord `00-principes.md`.

**Pourquoi une règle dédiée** : c'est ici que l'architecture se dégrade le plus facilement, sans bruit.
- `main.py` grossit jusqu'à contenir de la logique.
- `shared` devient un fourre-tout où atterrissent des règles métier « pour aller plus vite ».

## Composition root (`app/main.py` et `app/composition/`)

### Rôle
C'est le **seul endroit** du backend qui instancie des implémentations concrètes et les branche sur les ports (Dependency Injection).

### Règles
- `main.py` crée l'application FastAPI, enregistre les routeurs, les middlewares et le gestionnaire d'erreurs. **Rien d'autre.**
- Les fonctions fournisseurs (`fournir_signaler_etape_terminee()`…) sont rangées dans `app/composition/`, à raison d'un fichier par module. Elles ne font qu'assembler : aucun `if` métier, aucune requête. Elles peuvent contenir un **adaptateur de conversion** entre deux modules (par exemple `composition/resume_etapes.py`, qui recopie la vue d'un module dans le type attendu par le port de l'autre), sans aucune règle.
- La configuration est lue **une seule fois**, ici, via pydantic-settings (`Parametres`), puis transmise en paramètre. `os.environ` et `os.getenv` sont interdits partout ailleurs.
- L'ordre de la chaîne de contrôle des fichiers est défini ici, et nulle part ailleurs.
- Les commandes CLI (`app/cli/` : `creer-premier-chef`, purge RGPD) passent par les **mêmes** fonctions d'assemblage et les **mêmes** cas d'usage que l'API. Aucune logique propre à la CLI.
- Les tests peuvent remplacer une dépendance par `app.dependency_overrides`, mais uniquement dans les tests.

## Module `shared`

### Rôle
Fournir le code **technique** transverse, sans aucun concept métier. Il suit le même découpage en 4 parties :

| Partie | Contenu |
|---|---|
| `shared/domain` | `ErreurMetier` (classe de base), types d'identifiants, `Acteur` |
| `shared/application` | Ports transverses : `UnitOfWork`, `Horloge`, `GenerateurId` |
| `shared/infrastructure` | Moteur et session SQLAlchemy, UoW SQL et mémoire, horloge système, UUID v7, journalisation (règle 03) |
| `shared/api` | Gestionnaire central des erreurs, middlewares de protection (en-têtes, hôtes acceptés, taille, blocage, débit : ADR 0016 ; CSRF et identifiant de requête à venir), dépendance `acteur_courant` |

### Règles
- `shared` **n'importe aucun module métier** (`auth`, `chantiers`, `etapes`, `documents`, `rgpd`). Vérifié par import-linter.
- **Aucun mot du métier** dans `shared` : pas de `Chantier`, d'`Etape` ni de `Budget`. Si un concept est métier, il appartient à son module.
- On n'ajoute quelque chose dans `shared` que s'il est **déjà** utilisé par au moins deux modules. Sinon, il reste dans son module.
- Les mêmes règles de couche (`01` à `04`) s'appliquent à chaque partie de `shared`.

## Comment vérifier
- **Automatique** (`just verifier`) :
  - import-linter : « shared n'importe aucun module métier », « Seules la composition et les commandes importent une infrastructure » ;
  - tests dans `backend/tests/composition/` (paramètres, adaptateurs de conversion).
- **Par un agent** : `conformite` (aucun mot du métier dans `shared`, `main.py` sans logique, configuration lue une seule fois).
- **Pas encore vérifié** : aucun outil n'interdit `os.environ` hors de la composition.
