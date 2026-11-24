# ADR 0001 : monolithe modulaire en architecture hexagonale allégée

- **Statut** : accepté
- **Date** : 2026-11-22

## Contexte

- Une seule personne développe le projet, et il sera déployé sur un seul serveur auto-hébergé.
- Le métier contient de vraies règles : un cycle de validation des étapes, des droits par rôle et par affectation, et un calcul d'avancement.
- On veut pouvoir changer de base de données et de stockage sans réécrire le métier.
- Les tests doivent atteindre 100 % de couverture et un score de mutation élevé sur le métier.
- Plus tard viendront une application mobile, des devis et une facturation via un service externe.

## Décision

Le backend est un **monolithe modulaire**, découpé par fonctionnalité métier :
- `auth`, `chantiers`, `etapes`, `documents` et `rgpd` ;
- plus `shared` pour le code technique transverse.

Chaque module est organisé selon une **architecture hexagonale allégée** (*ports & adapters*) :

| Partie | Contenu | Peut dépendre de |
|---|---|---|
| `domain` | Entités, objets valeur, règles et erreurs métier, en Python pur | Bibliothèque standard |
| `application` | Services (cas d'usage) et ports | `domain` |
| `infrastructure` | Adaptateurs : SQL, disque, ClamAV, SMTP | `application`, `domain` |
| `api` | Routes FastAPI, schémas Pydantic | `application` |

Les règles de collaboration sont les suivantes :
- Un module n'utilise un autre module que via les services publics de sa partie `application`.
- Les implémentations sont assemblées dans une seule *composition root* (`app/main.py`), via le `Depends` de FastAPI.
- On ne crée un port que là où un remplacement est réellement prévu (base de données, stockage, antivirus, e-mail, hachage, facturation) ou nécessaire aux tests (horloge, identifiants).
- Les règles de dépendance sont vérifiées en CI par **import-linter** : contrats de couches par module et indépendance entre modules.

## Alternatives écartées

| Option | Raison du rejet |
|---|---|
| **Microservices** | Coût d'exploitation et de cohérence disproportionné pour une personne et un serveur. |
| **3 couches classiques, sans ports** | Le métier se retrouverait couplé à l'ORM : impossible de le tester sans base de données, et difficile de changer de base. |
| **Découpage par couche technique** (`services/`, `repositories/`, `routes/` globaux) | Mélange les sujets ; l'ajout des devis et de la facturation toucherait tout le code. |
| **Clean architecture complète** (une classe par cas d'usage, CQRS, *event sourcing*) | Beaucoup de code de cérémonie, sans besoin réel à cette échelle. |

## Conséquences

- Le métier est testable sans infrastructure, grâce aux adaptateurs en mémoire.
- Ajouter un domaine, comme les devis, revient à ajouter un module ; changer de prestataire revient à ajouter un adaptateur.
- Il faut écrire un peu plus de code au départ (ports et adaptateurs mémoire), une dépense acceptée.
- Les frontières sont vérifiées par la CI plutôt que par la seule discipline.
- Si un module devait un jour devenir un service séparé, ses frontières existent déjà.
