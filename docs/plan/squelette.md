# Phase 1 – Squelette livrable rapidement

**Décidé le 2026-11-22.** Cette phase passe **avant** les lots 01 à 09. Elle livre vite une application utile, en respectant les règles de `.claude/rules/`. Les lots 01 à 09 deviennent la phase 2 : chacun reprendra ce que le squelette a déjà livré au lieu de le refaire.

## Périmètre

**Ce que livre le squelette**
- **Créer, modifier et lister des chantiers** : nom, adresse, client, date de début, échéance et budget.
- **Des étapes par chantier**, qui suivent le cycle complet : `À faire` → `En cours` → `Terminée (à valider)` → `Validée`. Le refus, avec un commentaire obligatoire, renvoie l'étape en `En cours`. L'historique des changements est conservé.
- **L'avancement en pourcentage**, calculé à partir des étapes validées, affiché sur la liste et sur le détail.
- **Pas d'authentification dans l'application.** L'utilisateur choisit son **profil**, chef ou ouvrier, dans l'interface. Le métier reçoit cet `Acteur` en paramètre, comme prévu par la règle 02 : la vraie connexion de la phase 2 remplacera seulement la source de l'acteur, sans toucher aux règles métier.
- **Mise en ligne** sur le serveur Ubuntu, derrière le Caddy du serveur (HTTPS automatique Let's Encrypt), sur `chantier-ultra.ddns.net`. **Version de démonstration publique, sans mot de passe** (décision du propriétaire au moment de la mise en ligne).

**Ce qui est reporté à la phase 2**
- Les comptes, les invitations et le mot de passe oublié.
- Le cloisonnement par utilisateur : dans le squelette, toute personne qui ouvre le site voit tous les chantiers.
- Les notes, les photos et les documents, donc aussi ClamAV.
- Le RGPD complet : export, suppression, purge.
- Les tests de mutation, CodeQL et ZAP. (Trivy, gitleaks, pip-audit et pnpm audit ont été ajoutés à la CI en S4, à la demande du propriétaire.)

**Ce qui ne change pas** : les couches et import-linter ; ESLint (couches et design system Balise) ; le typage strict ; les limites contre le code spaghetti ; les commentaires en français ; le TDD avec 100 % de couverture sur le domaine et les services ; Alembic. PostgreSQL attend la phase 2 : SQLite pendant le squelette (ADR 0007).

**Risque accepté par le propriétaire du projet** : le site de démonstration est public, et n'importe qui peut agir en tant que chef. On n'y saisit **aucune donnée réelle**. Le HTTPS, la CSP, la limite de taille des requêtes et la documentation masquée restent en place.

## Lots du squelette

| Lot | Contenu | Agents | Dépend de |
|---|---|---|---|
| **S1 – Socle allégé** | Squelette backend et frontend, outils qualité essentiels (ruff, mypy, import-linter, ESLint, Vitest, Playwright), thème Balise, `/api/health`, `justfile`, Docker Compose de développement (PostgreSQL), pre-commit, CI simple (lint, typage, architecture, tests) | `dev-socle` (Sonnet, élevé) | — |
| **S2 – Chantiers et étapes** | Domaine `Chantier`, `Etape` (table des transitions), `HistoriqueEtape`, `Avancement` ; cas d'usage ; noyau partagé minimal (UoW, horloge, identifiants, erreurs) ; repositories SQL et migrations ; API ; écrans liste, création, détail, étapes et validation, avec le sélecteur de profil ; e2e | `dev-metier` (Opus, élevé), `dev-donnees`, `dev-api`, `dev-frontend` | S1 |
| **S3 – Mise en ligne** | Images de production, `docker-compose.prod.yml`, Caddy existant du serveur (HTTPS, en-têtes, limite de taille) ; pare-feu, fail2ban et sauvegarde chiffrée en phase 2 | `dev-socle` (Opus, élevé) | S2 |
| **S4 – Tableau de bord** | Page d'accueil de la maquette Balise : « À valider », cartes de chantier avec compteurs et délai, activité récente ; Équipe, Invitation et Recherche affichées « Bientôt » (issue #28, journal `journal/lot-S4.md`) | `dev-metier`, `dev-donnees`, `dev-frontend` | S2 |
| **S5 – Corrections de relecture** | Constats des issues #17 à #24, #29, #30 et #32 : verrou de version, unicité de l'ordre, erreurs RFC 9457 et 422 par champ, capacités via `/api/moi`, jscpd et pre-commit (issue #38, journal `journal/lot-S5.md`) | `dev-metier`, `dev-donnees`, `dev-frontend`, `dev-socle` | S4 |

Chaque lot suit le skill `lot` : plan validé, TDD, vérification par `revue`, `conformite` et `securite`, puis PR proposée.

## Critères d'acceptation du squelette

- [~] Je crée un chantier (✅ ; la modification est reportée), puis je le modifie ; il apparaît dans la liste avec son échéance et son avancement.
- [~] J'ajoute (✅), je modifie, je réordonne et je supprime (reportés) des étapes sur un chantier.
- [x] En profil ouvrier, je fais passer une étape de `À faire` à `En cours`, puis à `Terminée (à valider)`. Je ne peux ni valider ni refuser.
- [x] En profil chef, je valide une étape, ou je la refuse avec un commentaire obligatoire, ce qui la renvoie en `En cours`.
- [x] Toute transition non autorisée est refusée par l'API (409).
- [x] L'avancement est égal au nombre d'étapes validées divisé par le nombre total, et vaut 0 % s'il n'y a aucune étape.
- [~] L'historique de chaque étape indique qui (le profil), quoi et quand (✅ enregistré ; l'affichage est reporté).
- [x] Le budget n'est affiché qu'en profil chef.
- [x] L'interface est en français, responsive (360 et 1280 px) et suit le design system Balise.
- [x] Les contrats d'architecture, le typage strict, le lint et les tests passent en CI, avec 100 % de couverture sur le domaine et les services.
- [x] L'application est en ligne en HTTPS (`https://chantier-ultra.ddns.net`). Le mot de passe d'accès a été retiré : c'est une démonstration publique.

## Mise à jour du 2026-11-22 : un premier socle en 2 à 3 heures

À la demande du propriétaire du projet, le squelette est encore resserré, pour obtenir un premier socle en 2 à 3 heures.

- **Base de données : SQLite**, y compris en ligne pour ce premier socle. Le code passe par SQLAlchemy et Alembic : le passage à PostgreSQL se fera en phase 2, en changeant surtout la configuration.
- **Mise en ligne maintenue ce soir** (décision corrigée le même jour) : deux conteneurs (`chantier-api` avec la base SQLite dans un volume, `chantier-web` pour les fichiers statiques), placés derrière le Caddy déjà présent sur le serveur, qui gère le HTTPS. fail2ban, le pare-feu et la sauvegarde chiffrée sont reportés à la phase 2.
- **Le lot S2 est resserré** :
  - **inclus** : créer un chantier, lister les chantiers avec leur avancement, consulter le détail d'un chantier, ajouter des étapes, les faire avancer, les valider ou les refuser avec un commentaire, et choisir son profil. L'historique est enregistré à chaque transition ;
  - **reporté** : la modification et l'archivage d'un chantier, la modification, la suppression et le réordonnancement des étapes, et l'affichage de l'historique.
- **CI** : lint, typage, contrats d'architecture et tests ; depuis S4, aussi le job Sécurité (gitleaks, pip-audit, pnpm audit, Trivy) ; depuis S5, la duplication (jscpd) et le job Hooks git (pre-commit).

Critères du premier socle : ceux de la section ci-dessus, **sauf** la modification d'un chantier, la gestion avancée des étapes (modifier, réordonner, supprimer), et l'affichage de l'historique. La mise en ligne en HTTPS reste exigée ; le mot de passe d'accès a finalement été écarté pour la démonstration.

## Estimation

| Lot | Travail des agents |
|---|---|
| S1 | 2 à 3 h |
| S2 | 4 à 6 h |
| S3 | 2 à 3 h, plus ce qui dépend de l'utilisateur (nom de domaine, accès à la box et au serveur) |
| S4 | environ 2 h 30, vérifications et corrections comprises |
| S5 | environ 3 h, vérifications et corrections comprises |
| **Total** | **environ 1 à 1,5 jour de travail** |
