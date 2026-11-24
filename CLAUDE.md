# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

> **⚠️ OBLIGATOIRE : lis `intent.md` en entier au début de chaque session et avant chaque tâche, sans exception.** C'est la source de vérité du projet. En cas de contradiction avec ce fichier ou avec un autre document, c'est `intent.md` qui prévaut, et tu le signales à l'utilisateur.

## Règles de travail

- Travaille **uniquement sur la branche `dev`**. Vérifie la branche courante avant chaque commit.
- **Ne pousse jamais sur `main`, ne fusionne jamais dans `main`** et ne modifie jamais `main` sans l'autorisation explicite de l'utilisateur, demandée à chaque fois.
- `main` est protégée sur GitHub : le push direct, le force-push et la suppression sont interdits, y compris pour les admins. Le seul chemin vers `main` est une **pull request de `dev` vers `main`**. N'ouvre cette PR que si l'utilisateur le demande ; seul lui décide de la fusionner.
- **Ne démarre jamais un lot de développement de toi-même** : chaque lot ne commence que sur la demande explicite de l'utilisateur.
- Un lot se traite **toujours avec le skill `lot`** (`/lot NN`).
  - La session principale coordonne, en Opus 5.5 avec un effort élevé au minimum. Elle délègue le code aux sous-agents `dev-metier`, `dev-donnees`, `dev-api`, `dev-frontend` et `dev-socle`, puis fait vérifier le travail par `revue`, `conformite` et `securite` ; l'agent `pentest` attaque ensuite l'application qui tourne (skill `pentest`, règle 08).
  - Le skill fixe le modèle et l'effort de chaque agent.
  - Un commit `feat(lot-NN): <étape>` est fait par étape validée, sur `dev`.
  - À la fin du lot, la PR vers `main` est **proposée**, jamais ouverte sans accord.
- Le backlog vit dans les GitHub Issues (skill et agent `backlog`). Une idée ou un constat hors lot y devient une issue ; on ne le code pas.
- Dépôt : https://github.com/Nyulga/chantier-manager (public). N'y mets jamais de secret ni de donnée réelle de chantier ou de client.

## Documents de référence

- **`intent.md`** est la source de vérité : produit, architecture, contraintes, hors périmètre (section 4, à ne jamais réaliser) et critères d'acceptation (section 5).
- **`.claude/rules/`** : les règles **strictes** par couche. `00-principes.md` s'applique toujours (SOLID, limites chiffrées, commentaires en français, TDD) ; les règles `01` à `07` couvrent les couches `domain`, `application`, `infrastructure` et `api`, le frontend, la composition root avec `shared`, ainsi que les tests et migrations ; la règle `08` fixe les règles d'engagement des tests d'intrusion (périmètre, charge, rapports). **Avant de coder dans une couche, relis sa règle**, à chaque lot. Si une demande contredit une règle, signale-le au lieu de la contourner.
- **`docs/decisions/`** : les décisions d'architecture et leurs justifications. Toute décision structurante nouvelle ou modifiée donne lieu à un nouvel ADR.
- **`docs/design-system.md`** : le design system « Balise », validé. Toute interface l'applique, et ses tokens ne passent que par le thème Tailwind ; aucune couleur ni taille en dur. Le jaune haute visibilité et les rayures sont réservés aux étapes à valider (le jaune aussi au bouton principal sur mobile et à l'élément actif de la navigation).
- **`docs/plan/`** : le plan de développement en 9 lots verticaux (`README.md`, puis un fichier `lot-XX-*.md` par lot). Avant de travailler sur un lot, lis son fichier et respecte sa « définition de terminé ».

## État du projet

**Phase en cours : le squelette** ([`docs/plan/squelette.md`](docs/plan/squelette.md), lots S1 à S5). Il n'y a pas d'authentification dans l'application : l'`Acteur` vient d'un sélecteur de profil.


Les lots S1 (socle), S2 (chantiers et étapes), S3 (mise en ligne), S4 (tableau de bord) et S5 (corrections de relecture) sont livrés ; la base est **SQLite** pour l'instant (ADR 0007). Le déploiement est décrit dans `deploy/README.md` : deux conteneurs derrière le Caddy déjà présent sur le serveur.

## Commandes

Toutes passent par le `justfile` de la racine (Windows et Linux) :

| Commande | Rôle |
|---|---|
| `just installer` | `uv sync --locked` (backend), puis `pnpm install --frozen-lockfile` (frontend) |
| `just lancer` | l'API sur le port 8000 (avec `--reload`) et Vite, qui relaie `/api` vers l'API |
| `just verifier` | tous les contrôles de la CI : ruff, format, mypy, import-linter, limites de taille, bandit, pytest et couverture (100 % sur domain et application) ; ESLint, tsc, Prettier, Vitest et build ; duplication de code (`just doublons`) |
| `just test-back <chemin ou -k nom>` | un test backend précis, sans couverture (par exemple `just test-back tests/domain/etapes/test_cycle.py`) |
| `just test-front <motif>` | un test frontend précis (`vitest run <motif>`) |
| `just e2e` | Playwright à 360 et 1280 px, contre l'API réelle sur une base SQLite temporaire |
| `just client` | régénère `frontend/src/api/schema.d.ts` depuis le schéma OpenAPI de l'API |
| `just doublons` | duplication de code (jscpd) : 2 % au plus en production (Python et TypeScript), seuil séparé pour les tests TypeScript |
| `just hooks` | installe les hooks git (`.pre-commit-config.yaml`) : contrôles rapides au commit, tests et duplication au push |
| `just normaliser-fins-de-ligne` | réécrit en LF les fichiers restés en CRLF dans la copie de travail Windows (échoue s'il reste des modifications non indexées) |

Sous Windows, uv et just viennent de winget : si le shell ne les trouve pas, rafraîchis le `PATH`.

## Architecture

- `backend/` : API REST en Python 3.13+ avec FastAPI. `frontend/` : SPA React, TypeScript et Vite, servie sur le même domaine que l'API (`/api`). La future application mobile utilisera la même API, donc **aucune règle métier dans le frontend**.
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
- Les tests des services utilisent les implémentations mémoire (repositories, UoW, horloge, stockage). Les tests d'intégration utilisent un vrai PostgreSQL via testcontainers (SQLite pendant le squelette : ADR 0007).
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
