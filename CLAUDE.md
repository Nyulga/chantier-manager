# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

> **⚠️ OBLIGATOIRE : lis `intent.md` en entier au début de chaque session et avant chaque tâche, sans exception.** C'est la source de vérité du projet. En cas de contradiction avec ce fichier ou avec un autre document, c'est `intent.md` qui prévaut, et tu le signales à l'utilisateur.

## Règles de travail

- Travaille **uniquement sur la branche `dev`**. Vérifie la branche courante avant chaque commit.
- **Ne pousse jamais sur `main`, ne fusionne jamais dans `main`** et ne modifie jamais `main` sans l'autorisation explicite de l'utilisateur, demandée à chaque fois.
- `main` est protégée sur GitHub : le push direct, le force-push et la suppression sont interdits, y compris pour les admins. Le seul chemin vers `main` est une **pull request de `dev` vers `main`**. N'ouvre cette PR que si l'utilisateur le demande ; seul lui décide de la fusionner.
- **Ne démarre jamais un lot de développement de toi-même** : chaque lot ne commence que sur la demande explicite de l'utilisateur.
- Dépôt : https://github.com/Nyulga/chantier-manager (public). N'y mets jamais de secret ni de donnée réelle de chantier ou de client.

## Documents de référence

- **`intent.md`** est la source de vérité : produit, architecture, contraintes, hors périmètre (section 4, à ne jamais réaliser) et critères d'acceptation (section 5).
- **`.claude/rules/`** : les règles **strictes** par couche. `00-principes.md` s'applique toujours (SOLID, limites chiffrées, commentaires en français, TDD) ; les règles `01` à `07` couvrent les couches `domain`, `application`, `infrastructure` et `api`, le frontend, la composition root avec `shared`, ainsi que les tests et migrations. **Avant de coder dans une couche, relis sa règle**, à chaque lot. Si une demande contredit une règle, signale-le au lieu de la contourner.
- **`docs/adr/`** : les décisions d'architecture et leurs justifications. Toute décision structurante nouvelle ou modifiée donne lieu à un nouvel ADR.
- **`docs/design-system.md`** : le design system « Balise », validé. Toute interface l'applique, et ses tokens ne passent que par le thème Tailwind ; aucune couleur ni taille en dur. Le jaune haute visibilité et les rayures sont réservés aux étapes à valider.
- **`docs/plan/`** : le plan de développement en 9 lots verticaux (`README.md`, puis un fichier `lot-XX-*.md` par lot). Avant de travailler sur un lot, lis son fichier et respecte sa « définition de terminé ».

## État du projet

Seule la documentation existe pour l'instant ; aucun code n'a été écrit. Ajoute ici les commandes de build, de lint et de test (y compris celle qui lance un seul test) dès qu'elles existent, c'est-à-dire à la fin du lot 01.

## Architecture

- `backend/` : API REST en Python 3.12+ avec FastAPI. `frontend/` : SPA React, TypeScript et Vite, servie sur le même domaine que l'API (`/api`). La future application mobile utilisera la même API, donc **aucune règle métier dans le frontend**.
- Le backend est un **monolithe modulaire** : modules `auth`, `chantiers`, `etapes`, `documents`, `rgpd`, plus `shared` pour le code technique transverse.
- Chaque module est découpé en 4 parties :
  - `domain` : Python pur, sans FastAPI, SQLAlchemy ni Pydantic ;
  - `application` : services et ports (interfaces) ;
  - `infrastructure` : implémentations des ports ;
  - `api` : routes et schémas, sans logique métier.
- Dépendances autorisées :
  - `api` → `application` → `domain` ;
  - `infrastructure` → `application`/`domain` ;
  - entre modules : uniquement via la partie `application` de l'autre module.
  Ces règles sont imposées par des **contrats import-linter** ; ne les contourne pas.
- Les implémentations sont assemblées **uniquement** dans la *composition root* (`app/main.py`), via le `Depends` de FastAPI.
- Persistance :
  - SQLAlchemy 2 **en mode synchrone**, avec un **mapping impératif** : les entités du domaine sont des dataclasses, sans classe ORM en double ;
  - chaque cas d'usage passe par l'interface `UnitOfWork`, qui a une implémentation SQL et une implémentation mémoire (pour les tests) ;
  - le schéma ne change jamais sans migration Alembic ;
  - identifiants en UUID v7 ; montants en `Decimal`, jamais en `float`.
- Les tests des services utilisent les implémentations mémoire (repositories, UoW, horloge, stockage). Les tests d'intégration utilisent un vrai PostgreSQL via testcontainers.
- Les types TypeScript du frontend sont **générés depuis le schéma OpenAPI**. Ne les écris jamais à la main.

## Règles métier qui traversent plusieurs couches

- Cycle d'une étape : `À faire` → `En cours` → `Terminée (à valider)` (ouvrier) → `Validée` (chef du chantier uniquement).
  - Un refus, réservé au chef et accompagné d'un commentaire obligatoire, renvoie l'étape en `En cours`.
  - Toute autre transition lève `TransitionInterdite`.
  - Chaque transition écrit une entrée d'historique, dans la même transaction.
- Avancement = étapes validées / nombre total d'étapes, et 0 % s'il n'y a aucune étape. Il est toujours calculé, jamais stocké.
- Cloisonnement : un utilisateur, **chef comme ouvrier**, n'accède qu'aux chantiers auxquels il est rattaché. Pour un chantier hors de son périmètre, l'API répond 404. Le budget n'est visible que par les chefs du chantier.
- Les droits sont vérifiés dans les services, via les politiques d'accès pures du domaine. Ces politiques sont testées par une matrice exhaustive rôle × action × affectation.
- Comptes :
  - aucune inscription publique ; le premier chef est créé en CLI, les autres utilisateurs sont invités par e-mail ;
  - les tokens d'invitation, de réinitialisation et de refresh sont à usage unique et stockés hachés ;
  - un refresh token réutilisé révoque toute la session.
- Fichiers :
  - formats et tailles : PDF (20 Mo) ; photos JPEG, PNG, WebP et HEIC (10 Mo) ;
  - chaîne de contrôle, dans cet ordre : taille → *magic bytes* → ClamAV (antivirus indisponible = envoi refusé) → réencodage des photos sans EXIF → nom aléatoire et stockage hors du dossier public ;
  - les fichiers ne sont servis que par l'API, après vérification des droits.

## Exigences non négociables

- Typage : mypy `--strict` et TypeScript `strict`, sans `any`.
- Couverture : 100 % sur le domaine et les services, au moins 95 % sur tout le backend (lignes et branches), au moins 90 % sur le frontend. Score de mutation d'au moins 90 % sur le domaine et les services (mutmut, en CI Linux). Utilise le TDD pour les règles métier.
- Sécurité selon OWASP ASVS niveau 2. Le détail est dans la section 3.2 d'`intent.md`.
- Interface en français uniquement, responsive et conçue d'abord pour le mobile, accessible au niveau WCAG 2.1 AA.
- RGPD : minimisation des données, export et suppression des données d'un utilisateur, durées de conservation avec purge automatique.
