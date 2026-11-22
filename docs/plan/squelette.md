# Phase 1 – Squelette livrable rapidement

**Décidé le 2026-11-22.** Cette phase passe **avant** les lots 01 à 09. Elle livre vite une application utile, en respectant les règles de `.claude/rules/`. Les lots 01 à 09 deviennent la phase 2 : chacun reprendra ce que le squelette a déjà livré au lieu de le refaire.

## Périmètre

**Ce que livre le squelette**
- **Créer, modifier et lister des chantiers** : nom, adresse, client, date de début, échéance et budget.
- **Des étapes par chantier**, qui suivent le cycle complet : `À faire` → `En cours` → `Terminée (à valider)` → `Validée`. Le refus, avec un commentaire obligatoire, renvoie l'étape en `En cours`. L'historique des changements est conservé.
- **L'avancement en pourcentage**, calculé à partir des étapes validées, affiché sur la liste et sur le détail.
- **Pas d'authentification dans l'application.** L'utilisateur choisit son **profil**, chef ou ouvrier, dans l'interface. Le métier reçoit cet `Acteur` en paramètre, comme prévu par la règle 02 : la vraie connexion de la phase 2 remplacera seulement la source de l'acteur, sans toucher aux règles métier.
- **Mise en ligne** sur le serveur Ubuntu, derrière un **mot de passe d'accès au site** géré par Caddy (HTTPS automatique Let's Encrypt), sur `chantier-ultra.ddns.net`.

**Ce qui est reporté à la phase 2**
- Les comptes, les invitations et le mot de passe oublié.
- Le cloisonnement par utilisateur : dans le squelette, toute personne qui a le mot de passe du site voit tous les chantiers.
- Les notes, les photos et les documents, donc aussi ClamAV.
- Le RGPD complet : export, suppression, purge.
- Les tests de mutation, CodeQL, Trivy, ZAP et les audits.

**Ce qui ne change pas** : les couches et import-linter ; ESLint (couches et design system Balise) ; le typage strict ; les limites contre le code spaghetti ; les commentaires en français ; le TDD avec 100 % de couverture sur le domaine et les services ; PostgreSQL et Alembic.

**Risque accepté par le propriétaire du projet** : toute personne qui connaît le mot de passe du site peut agir en tant que chef. On n'y met donc aucune donnée sensible au-delà de ce qu'exige le suivi des chantiers.

## Lots du squelette

| Lot | Contenu | Agents | Dépend de |
|---|---|---|---|
| **S1 – Socle allégé** | Squelette backend et frontend, outils qualité essentiels (ruff, mypy, import-linter, ESLint, Vitest, Playwright), thème Balise, `/api/health`, `justfile`, Docker Compose de développement (PostgreSQL), pre-commit, CI simple (lint, typage, architecture, tests) | `dev-socle` (Sonnet, élevé) | — |
| **S2 – Chantiers et étapes** | Domaine `Chantier`, `Etape` (table des transitions), `HistoriqueEtape`, `Avancement` ; cas d'usage ; noyau partagé minimal (UoW, horloge, identifiants, erreurs) ; repositories SQL et migrations ; API ; écrans liste, création, détail, étapes et validation, avec le sélecteur de profil ; e2e | `dev-metier` (Opus, élevé), `dev-donnees`, `dev-api`, `dev-frontend` | S1 |
| **S3 – Mise en ligne** | Images de production, `docker-compose.prod.yml`, Nginx (HTTPS, mot de passe d'accès, en-têtes), pare-feu, fail2ban, sauvegarde quotidienne chiffrée de la base | `dev-socle` (Opus, élevé) | S2 |

Chaque lot suit le skill `lot` : plan validé, TDD, vérification par `revue`, `conformite` et `securite`, puis PR proposée.

## Critères d'acceptation du squelette

- [ ] Je crée un chantier, puis je le modifie ; il apparaît dans la liste avec son échéance et son avancement.
- [ ] J'ajoute, je modifie, je réordonne et je supprime des étapes sur un chantier.
- [ ] En profil ouvrier, je fais passer une étape de `À faire` à `En cours`, puis à `Terminée (à valider)`. Je ne peux ni valider ni refuser.
- [ ] En profil chef, je valide une étape, ou je la refuse avec un commentaire obligatoire, ce qui la renvoie en `En cours`.
- [ ] Toute transition non autorisée est refusée par l'API (409).
- [ ] L'avancement est égal au nombre d'étapes validées divisé par le nombre total, et vaut 0 % s'il n'y a aucune étape.
- [ ] L'historique de chaque étape indique qui (le profil), quoi et quand.
- [ ] Le budget n'est affiché qu'en profil chef.
- [ ] L'interface est en français, responsive (360 et 1280 px) et suit le design system Balise.
- [ ] Les contrats d'architecture, le typage strict, le lint et les tests passent en CI, avec 100 % de couverture sur le domaine et les services.
- [ ] L'application est en ligne en HTTPS, et inaccessible sans le mot de passe du site.

## Mise à jour du 2026-11-22 : un premier socle en 2 à 3 heures

À la demande du propriétaire du projet, le squelette est encore resserré, pour obtenir un premier socle en 2 à 3 heures.

- **Base de données : SQLite**, y compris en ligne pour ce premier socle. Le code passe par SQLAlchemy et Alembic : le passage à PostgreSQL se fera en phase 2, en changeant surtout la configuration.
- **Mise en ligne maintenue ce soir** (décision corrigée le même jour) : deux conteneurs (`chantier-api` avec la base SQLite dans un volume, `chantier-web` pour les fichiers statiques), placés derrière le Caddy déjà présent sur le serveur, qui gère le HTTPS et le mot de passe d'accès. fail2ban, le pare-feu et la sauvegarde chiffrée sont reportés à la phase 2.
- **Le lot S2 est resserré** :
  - **inclus** : créer un chantier, lister les chantiers avec leur avancement, consulter le détail d'un chantier, ajouter des étapes, les faire avancer, les valider ou les refuser avec un commentaire, et choisir son profil. L'historique est enregistré à chaque transition ;
  - **reporté** : la modification et l'archivage d'un chantier, la modification, la suppression et le réordonnancement des étapes, et l'affichage de l'historique.
- **CI** : lint, typage, contrats d'architecture et tests uniquement.

Critères du premier socle : ceux de la section ci-dessus, **sauf** la modification d'un chantier, la gestion avancée des étapes (modifier, réordonner, supprimer), et l'affichage de l'historique. La mise en ligne en HTTPS, protégée par le mot de passe du site, reste exigée.

## Estimation

| Lot | Travail des agents |
|---|---|
| S1 | 2 à 3 h |
| S2 | 4 à 6 h |
| S3 | 2 à 3 h, plus ce qui dépend de l'utilisateur (nom de domaine, accès à la box et au serveur) |
| **Total** | **environ 1 à 1,5 jour de travail** |
