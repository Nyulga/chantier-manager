# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Règles de travail

- Travaille **uniquement sur la branche `dev`**. Vérifie la branche courante avant chaque commit.
- **Ne pousse jamais sur `main`, ne fusionne jamais dans `main`** et ne modifie jamais `main` sans l'autorisation explicite de l'utilisateur, demandée à chaque fois.

## État du projet

Le projet en est au stade de la spécification : aucun code n'existe encore. **`intent.md` est la source de vérité** pour le produit, l'architecture, les contraintes, le hors périmètre et les critères d'acceptation. Lis-le avant toute tâche, et ne réalise rien qui soit listé dans sa section 4 (Hors périmètre).

Le développement suit les lots convenus avec l'utilisateur : (1) socle, (2) domaine et base de données, (3) authentification et rôles, (4) chantiers et affectations, (5) étapes et avancement, (6) notes, photos et documents, (7) frontend responsive, (8) RGPD, (9) déploiement. Un lot n'est terminé que s'il respecte les critères de la section 5 d'`intent.md`.

Ajoute ici les commandes de build, de lint et de test (y compris celle qui lance un seul test) dès qu'elles existent, c'est-à-dire à la fin du lot 1.

## Architecture prévue

- `backend/` : API REST en Python 3.12+ avec FastAPI. `frontend/` : React, TypeScript et Vite. La future application mobile consommera la même API ; aucune logique métier ne doit donc vivre dans le frontend.
- Le backend est organisé en couches : **présentation** (routes FastAPI et schémas Pydantic, sans logique métier), **service** (règles métier et **vérification des droits à chaque opération**) et **données** (repositories).
- Le domaine (`Chantier`, `Etape`, `Note`, `Document`, `Utilisateur`) ne dépend ni de FastAPI ni de SQLAlchemy.
- Les services dépendent d'**interfaces** (repositories, `FileStorage`), jamais d'implémentations concrètes. Les implémentations SQLAlchemy et `LocalFileStorage` sont injectées. Les tests des services utilisent de faux repositories en mémoire.
- Base de données PostgreSQL, avec SQLAlchemy 2 et les migrations Alembic. Le schéma ne change jamais sans migration.
- Les types TypeScript du frontend sont **générés depuis le schéma OpenAPI**. Ne les écris jamais à la main.

## Règles métier qui traversent plusieurs couches

- Cycle d'une étape : `À faire` → `En cours` → `Terminée (à valider)` (ouvrier) → `Validée` (chef uniquement). Un refus, réservé au chef et accompagné d'un commentaire obligatoire, renvoie l'étape en `En cours`. Toute autre transition est rejetée par la couche service, et chaque transition est enregistrée dans l'historique.
- Avancement = étapes validées / nombre total d'étapes, et 0 % s'il n'y a aucune étape.
- Un ouvrier n'accède qu'aux chantiers auxquels il est affecté, et ne voit jamais le budget.
- Les fichiers sont limités aux PDF (20 Mo) et aux photos JPEG, PNG, WebP et HEIC (10 Mo). Le format est vérifié par les *magic bytes*. Les photos sont réencodées sans métadonnées EXIF. Les fichiers portent un nom aléatoire, sont stockés hors du dossier public et ne sont servis que par l'API après vérification des droits.

## Exigences non négociables

- Typage : mypy `--strict` et TypeScript `strict`, sans `any`.
- Couverture : 100 % sur le domaine et les services, au moins 95 % sur tout le backend (lignes et branches), au moins 90 % sur le frontend. Score de mutation d'au moins 90 % sur les services. Utilise le TDD pour les règles métier.
- Sécurité selon OWASP ASVS niveau 2 : Argon2id, JWT en cookies `HttpOnly`, `Secure` et `SameSite=Strict` avec protection CSRF, limitation des tentatives de connexion, CSP stricte. Le détail est dans la section 3.2 d'`intent.md`.
- Interface en français uniquement, responsive et conçue d'abord pour le mobile, accessible au niveau WCAG 2.1 AA.
- RGPD : minimisation des données, export et suppression des données d'un utilisateur, durées de conservation définies.
