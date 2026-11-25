# Intent

> Documents liés : [décisions d'architecture (ADR)](docs/decisions/) · [plan de développement par lots](docs/plan/README.md) · [règles par couche](.claude/rules/)

## 1. Produit

### Pitch
Application simple de gestion de chantiers qui permet de suivre l'état d'avancement de chaque chantier et d'y centraliser les informations du terrain : notes, photos, documents et adresse.

### Utilisateurs et rôles
| Rôle | Ce qu'il peut faire |
|---|---|
| **Chef de chantier** | Crée des chantiers ; sur **ses** chantiers (créés par lui ou auxquels il est affecté) : modifie, archive, affecte les chefs et les ouvriers, définit les étapes, valide ou refuse les étapes, voit le budget. Invite de nouveaux utilisateurs (ouvriers ou chefs). |
| **Ouvrier** | Consulte les chantiers auxquels il est affecté, fait avancer les étapes jusqu'à « Terminée (à valider) », ajoute des notes, des photos et des documents. |

**Cloisonnement** : personne ne voit un chantier auquel il n'est pas rattaché, chef comme ouvrier.

### Fonctionnalités clés (V1)
1. **Chantiers** : créer, modifier et archiver un chantier (nom, adresse, client, date de début, **échéance**, **budget / prix**). Le budget n'est visible que par les chefs du chantier.
2. **État d'avancement par étapes** : chaque chantier a une liste d'étapes qui suit ce cycle :
   `À faire` → `En cours` → `Terminée (à valider)`, signalée par l'ouvrier → `Validée` par un chef du chantier.
   Le chef peut aussi refuser une étape signalée terminée ; elle repasse alors `En cours`, avec un commentaire obligatoire.
   Chaque changement est enregistré dans l'historique de l'étape.
   Le pourcentage d'avancement du chantier se calcule à partir des étapes **validées** uniquement.
3. **Notes** : ajout de notes datées et signées par leur auteur, affichées sous forme de fil.
4. **Photos et documents** : envoi de fichiers (photos, PDF, plans) rattachés à un chantier.
5. **Comptes et accès**
   - Pas d'inscription publique.
   - Le **premier chef** est créé par une commande sur le serveur.
   - Un chef **invite** un nouvel utilisateur par e-mail : un lien à usage unique et à durée limitée permet à l'invité de définir son mot de passe.
   - **Mot de passe oublié** : un lien de réinitialisation est envoyé par e-mail.
   - Connexion et déconnexion ; chaque utilisateur ne voit que les chantiers qui le concernent.

### Phase 1 : squelette livré en premier
Avant la V1 complète, on livre un **squelette** utilisable rapidement : créer et suivre des chantiers, avec leurs étapes, leur validation et leur pourcentage d'avancement. Il n'y a pas d'authentification dans l'application : on choisit son profil (chef ou ouvrier) dans l'interface. Le site en ligne est une démonstration publique, sans mot de passe : on n'y saisit aucune donnée réelle. Le périmètre exact, ce qui est reporté et les critères sont dans [`docs/plan/squelette.md`](docs/plan/squelette.md). Toutes les règles de `.claude/rules/` s'y appliquent. Les autres sections de ce document décrivent la V1 complète (phase 2).

### Périmètre de la V1
Le produit aura à terme deux parties : une **application web** et une **application mobile**.
La V1 couvre **uniquement l'application web**. L'application mobile viendra plus tard (voir Hors périmètre).

## 2. Architecture

Les décisions détaillées, avec les alternatives écartées, sont dans [`docs/decisions/`](docs/decisions/).

### 2.1 Principe général
- Un **backend** qui expose une API REST et porte **toutes** les règles métier.
- Un **frontend web** (SPA) qui consomme cette API. Il ne contient aucune règle métier.
- La future application mobile consommera la même API.
- Le frontend et l'API sont servis **sur le même domaine** (l'API sous `/api`) : pas de CORS à ouvrir, et des cookies `SameSite=Strict` qui fonctionnent sans contournement.

### 2.2 Backend : monolithe modulaire, en architecture hexagonale allégée
Un seul backend déployable, découpé en **modules métier** :

| Module | Responsabilité |
|---|---|
| `auth` | Utilisateurs, rôles, mots de passe, sessions, invitations, réinitialisation |
| `chantiers` | Chantiers, affectations, politiques d'accès |
| `etapes` | Étapes, cycle de validation, historique, avancement |
| `documents` | Notes, photos et documents |
| `rgpd` | Export, suppression et anonymisation, purge, journal des actions sensibles |
| `shared` | Code technique transverse : configuration, base de données, Unit of Work, horloge, identifiants, erreurs, sécurité HTTP |

Chaque module est organisé en 4 parties :

| Partie | Contenu | Peut dépendre de |
|---|---|---|
| `domain` | Entités, objets valeur, règles et erreurs métier, en **Python pur** | Bibliothèque standard uniquement |
| `application` | Services (cas d'usage) et **interfaces (ports)** dont ils ont besoin | `domain` |
| `infrastructure` | Implémentations des ports : SQLAlchemy, disque, ClamAV, SMTP… | `application`, `domain` |
| `api` | Routes FastAPI et schémas Pydantic, sans aucune logique métier | `application` |

**Règles de dépendance**
- Le domaine n'importe ni FastAPI, ni SQLAlchemy, ni Pydantic.
- Un module n'utilise un autre module **que via ses services publics** (sa partie `application`), jamais via son domaine ou son infrastructure. Exemple : `etapes` demande à `chantiers` si un utilisateur est affecté au chantier.
- Ces règles sont **vérifiées automatiquement en CI** par **import-linter**. Une violation fait échouer la CI.
- Les implémentations sont assemblées à **un seul endroit** (la *composition root*, `app/main.py`), via l'injection de dépendances de FastAPI.

**Ce que ça permet**
- **Changer de base de données ou de stockage de fichiers** sans toucher au métier : il suffit d'écrire une nouvelle implémentation du port.
- **Tester le métier sans base de données**, grâce aux implémentations en mémoire.
- **Ajouter plus tard les devis et la facturation** comme de nouveaux modules. La facturation passera par un port `FacturationProvider`, qu'implémentera le service externe choisi.

### 2.3 Domaine
- **`Chantier`** (agrégat) : nom, `Adresse` (objet valeur), client, date de début, échéance, budget (objet valeur `Montant`, en `Decimal`, jamais en `float`), statut actif ou archivé, chefs affectés, ouvriers affectés.
- **`Etape`** : une **machine à états explicite**, avec une table des transitions autorisées par rôle. Une action que le rôle n'a jamais le droit de faire lève `AccesRefuse` (403) ; toute autre transition absente de la table lève `TransitionInterdite` (409). Chaque transition ajoute une entrée `HistoriqueEtape` (qui, quoi, quand, commentaire).
- **Avancement** : toujours **calculé** (étapes validées / total, et 0 % si aucune étape), jamais stocké.
- **Politiques d'accès** : fonctions pures du domaine (`peut_voir`, `peut_modifier`, `peut_valider`…), appelées par **chaque** service.
- **Erreurs métier typées** (`TransitionInterdite`, `AccesRefuse`, `NonTrouve`…), traduites en codes HTTP uniquement dans la partie `api`.
- **Identifiants** : UUID v7, fournis au domaine par le port `GenerateurId`. Ils sont triables et ne révèlent pas le nombre d'enregistrements.
- **Ports techniques** : `Horloge`, `GenerateurId`, `HacheurMotDePasse`, `StockageFichiers`, `ScanneurAntivirus`, `EnvoiEmail`, `UnitOfWork`, `JournalAudit` (disponible dès le noyau partagé, pour journaliser les actions sensibles dès leur création), plus un repository par agrégat.
- **Avancement affiché sur les chantiers** : `chantiers` déclare un port `FournisseurResumeEtapes` (avancement et compteurs d'étapes), que la composition root branche sur le calcul du module `etapes`. Aucun module n'importe donc l'autre dans les deux sens.
- **Concurrence** : chaque étape porte un numéro de version (verrou optimiste). Deux actions simultanées sur la même étape ne s'écrasent jamais : la seconde est rejetée (409).

### 2.4 Persistance
- **PostgreSQL 16+**, via **SQLAlchemy 2 en mode synchrone** (avec le pilote psycopg 3).
  - Le mode async a été écarté : il complique le chargement des relations et les tests, sans gain réel à cette échelle.
- **Mapping impératif** : les entités du domaine sont des dataclasses, que SQLAlchemy enregistre directement en base, sans classe ORM en double.
- **Unit of Work** : chaque cas d'usage s'exécute dans une transaction. Exemple : la validation d'une étape et l'écriture de son historique sont atomiques.
- **Alembic** pour toutes les évolutions du schéma.

### 2.5 Authentification
- Mots de passe hachés en **Argon2id**.
- **JWT d'accès** de 15 minutes, et **refresh token opaque** stocké haché en base, avec **rotation**. Un refresh token réutilisé **révoque toute la session**.
- Web : tokens en cookies `HttpOnly`, `Secure` et `SameSite=Strict`, avec un token CSRF (*double submit*). Le mobile, plus tard, utilisera la même API avec un en-tête `Authorization`.
- **Invitations et réinitialisations** : token aléatoire à usage unique, stocké haché en base, à durée limitée, envoyé par le port `EnvoiEmail` (SMTP).

### 2.6 Fichiers
Un fichier envoyé passe par une chaîne de contrôle, dans cet ordre :
1. **Limite de taille**, appliquée par Nginx et par l'API pendant la lecture du flux.
2. **Vérification du format réel** grâce aux *magic bytes*.
3. **Analyse antivirus ClamAV**.
4. Pour les photos : **réencodage**, avec suppression des métadonnées EXIF.
5. **Nom aléatoire** et stockage hors de la racine web.

Les fichiers ne sont servis que par l'API, après vérification des droits. Les PDF sont toujours téléchargés, jamais affichés dans la page (`Content-Disposition: attachment`, `CSP: sandbox`).

### 2.7 Frontend
- SPA **React + TypeScript (Vite)**, organisée par fonctionnalité (`src/features/chantiers/…`).
- **Client API généré** depuis le schéma OpenAPI (openapi-typescript et openapi-fetch).
- **TanStack Query** pour les données serveur, **React Router**, et **react-hook-form + zod** pour les formulaires.
- **Tailwind CSS** et composants **Radix** (accessibles par défaut).

### 2.8 Choix techniques
| Élément | Choix |
|---|---|
| Backend | Python 3.13+, FastAPI, Pydantic v2, pydantic-settings |
| Persistance | PostgreSQL 16+, SQLAlchemy 2 (synchrone, mapping impératif), Alembic, psycopg 3 |
| Sécurité | argon2-cffi, PyJWT, filetype, Pillow et pillow-heif, ClamAV (clamd) |
| Logs | structlog (format JSON, identifiant de requête, aucune donnée personnelle) |
| Frontend | React, TypeScript, Vite, TanStack Query, React Router, react-hook-form, zod, Tailwind CSS, Radix |
| Outils | uv (Python), pnpm (frontend), just (lanceur de commandes, Windows et Linux), Docker Compose |
| Tâches planifiées | Commandes CLI (purge RGPD, sauvegardes) lancées par un timer systemd ou cron ; pas de file de tâches |

### 2.9 Design patterns et principes
- Les principes **SOLID** sont obligatoires, avec une traduction vérifiable pour chacun (voir [`.claude/rules/00-principes.md`](.claude/rules/00-principes.md)).
- Chaque couche a sa **règle**, avec ses patterns obligatoires et ses interdits, dans [`.claude/rules/`](.claude/rules/). Ces règles s'appliquent à **chaque lot**. Justification : [ADR 0005](docs/decisions/0005-design-patterns-et-garde-fous.md).
- Chaque couche a un rôle unique :
  - la présentation (`api` et frontend) n'appelle que la couche service ;
  - la couche service (`application`), s'appuyant sur le `domain`, porte les règles métier, et ses tests sont écrits avant le code ;
  - seule l'`infrastructure` parle à la base de données et aux services externes.
- Le frontend suit le sens d'appel `pages` → `services` → `api`, et n'affiche **que** des composants du design system (`src/ui`).
- Anti-patterns interdits : Singleton, Service Locator, Active Record, modèle anémique, god object, pattern sans besoin réel.

### 2.10 Déploiement
- **Serveur Ubuntu personnel**, hébergé à domicile en France.
- **Docker Compose** :
  - en production : `api`, `web`, `db` (PostgreSQL), `clamav`, plus des volumes pour les données et les fichiers ;
  - en développement : PostgreSQL, ClamAV et **Mailpit**, qui intercepte les e-mails.
- **Nginx** en reverse proxy, **HTTPS** via Let's Encrypt.
- **SMTP** d'un fournisseur établi dans l'UE, pour les e-mails de sécurité uniquement.
- Sauvegardes régulières et chiffrées de la base de données et du dossier de fichiers, avec **au moins une copie hors du domicile**, stockée dans l'UE (en cas de panne, de vol ou d'incendie).
- Auto-hébergement à domicile : seuls les ports 80 et 443 sont redirigés depuis la box ; SSH est accessible uniquement par clé (ou via VPN) ; fail2ban est actif ; le serveur et la box reçoivent des mises à jour de sécurité automatiques.

## 3. Contraintes

### 3.1 Qualité du code
**Typage strict partout**
- Backend : annotations de type obligatoires et **mypy en mode `--strict`**, aucun `Any` implicite.
- Frontend : **TypeScript `strict: true`**, avec `noUncheckedIndexedAccess` et `exactOptionalPropertyTypes` ; `any` interdit par lint.
- Les types du frontend sont **générés automatiquement depuis le schéma OpenAPI** de l'API, pour qu'aucun décalage ne soit possible entre le front et le back.

**Architecture et lisibilité (aucun code spaghetti, aucun fichier fourre-tout)**
- Les contrats **import-linter** (couches, indépendance des modules, accès à la base réservé à l'`infrastructure`) passent en CI. Côté frontend, ESLint impose le sens des dépendances et l'usage exclusif du design system.
- Limites vérifiées automatiquement :
  - au plus 300 lignes par fichier Python et 250 par fichier TypeScript ;
  - au plus 40 lignes par fonction Python et 60 par fonction TypeScript ;
  - complexité cyclomatique d'au plus 8 ;
  - au plus 3 niveaux d'imbrication ;
  - au plus 2 % de code dupliqué ;
  - aucun import circulaire.
- La désactivation d'une règle de lint, de typage ou de couverture est interdite sans l'accord du propriétaire du projet.

**Commentaires**
- Le code est commenté **en français**, en phrases claires et bien écrites.
- Chaque fichier et chaque classe publique décrit son rôle, et chaque règle métier ou choix non évident est expliqué : on écrit le *pourquoi*, pas une paraphrase du code.
- Détail dans `.claude/rules/00-principes.md` (§7).

**Lint et formatage**
- Backend : **ruff** (lint et formatage), **bandit** pour l'analyse de sécurité.
- Frontend : **ESLint** (règles strictes, `typescript-eslint` en mode strict) et **Prettier**.
- **Hooks pre-commit** : aucun commit possible si le lint, le typage ou les tests échouent.

**Tests**
| Niveau | Outils | Objectif |
|---|---|---|
| Unitaires (domaine et services) | pytest, hypothesis (tests par propriétés sur la machine à états) | **100 %** des lignes et des branches |
| Intégration (API et base réelle) | pytest + httpx + PostgreSQL en conteneur (testcontainers) | Toutes les routes, y compris les cas d'erreur et de refus d'accès |
| Frontend | Vitest + Testing Library | ≥ 90 % |
| Bout en bout | Playwright | Les parcours critiques de chaque rôle |
| Robustesse des tests | mutmut (tests de mutation) sur le domaine et les services, exécuté en CI Linux | Vérifier que les tests détectent vraiment les erreurs |

- Couverture globale du backend **≥ 95 %, lignes et branches**. La CI échoue en dessous de ce seuil.
- Développement piloté par les tests (TDD) pour les règles métier.
- Les politiques d'accès sont testées par une **matrice exhaustive** rôle × action × affectation.

**Intégration continue (GitHub Actions)**
- Chaque push lance le lint, le typage, les contrats d'architecture, les tests, la couverture, les tests de mutation et les audits de sécurité.
- Ces jobs sont des **checks obligatoires** pour fusionner dans `main`.

### 3.2 Sécurité (tolérance zéro)
Référentiel : **OWASP ASVS niveau 2** et **OWASP Top 10**.

**Authentification et mots de passe**
- Hachage **Argon2id**.
- Politique : **12 caractères minimum**, refus des mots de passe courants ou déjà apparus dans des fuites (liste locale), aucune limite maximale abusive.
- **Limitation des tentatives** de connexion (par IP et par compte), avec un blocage temporaire progressif.
- Token d'accès JWT de courte durée (15 min), refresh token opaque avec **rotation**, révocation et **détection de réutilisation**.
- Sur le web : tokens stockés en **cookies `HttpOnly`, `Secure`, `SameSite=Strict`**, avec une protection CSRF.
- Liens d'invitation et de réinitialisation : à usage unique, valables peu de temps, stockés hachés.
- La demande de réinitialisation renvoie toujours la même réponse, que le compte existe ou non (pas d'énumération des comptes).

**Autorisations**
- Les droits sont vérifiés **dans la couche service** à chaque opération, jamais seulement dans l'interface.
- Refus par défaut : un utilisateur (chef ou ouvrier) n'accède qu'aux chantiers auxquels il est rattaché.

**Fichiers envoyés**
- Formats autorisés : **PDF, JPEG, PNG, WebP, HEIC**. Le format est vérifié par le contenu réel du fichier (*magic bytes*), pas par l'extension.
- Taille maximale : **10 Mo par photo et 20 Mo par PDF**.
- **Analyse antivirus ClamAV** de chaque fichier. Si l'antivirus est indisponible, le fichier est **refusé**, jamais accepté sans analyse.
- Les photos sont **réencodées côté serveur**, et leurs **métadonnées EXIF sont supprimées** (dont la position GPS).
- Les fichiers sont renommés avec un identifiant aléatoire, stockés hors du dossier public et **servis uniquement par l'API après vérification des droits**.

**Application et infrastructure**
- Validation stricte de toutes les entrées (Pydantic) et requêtes SQL paramétrées uniquement, via l'ORM.
- En-têtes de sécurité : CSP stricte, HSTS, X-Content-Type-Options, Referrer-Policy, Permissions-Policy. Pas de CORS, puisque le front et l'API sont sur la même origine.
- HTTPS obligatoire.
- Aucun secret dans le dépôt : variables d'environnement, `.env` exclu de git, `.env.example` versionné.
- Audit des dépendances en CI (**pip-audit**, **pnpm audit**), analyse **CodeQL**, scan des images Docker avec **Trivy**, recherche de secrets avec **gitleaks**, et mises à jour suivies par Dependabot.
- Journal des actions sensibles (connexions, invitations, validations, suppressions), sans aucune donnée sensible dans les logs.
- Conteneurs exécutés sans droits root ; pare-feu limité aux ports 80 et 443, plus SSH.

### 3.3 RGPD
- **Minimisation** : on ne collecte que les données nécessaires.
- Hébergement **en France** (UE), sur un serveur personnel auto-hébergé à domicile ; fournisseur SMTP et sauvegardes externes **dans l'UE**.
- Droits des personnes : **accès, rectification, export et suppression** du compte et des données.
- **Durées de conservation** définies (par exemple pour les chantiers archivés, les journaux et les invitations expirées), avec une purge automatique.
- Page **politique de confidentialité** et **mentions légales**.
- Registre des traitements tenu à jour.
- Sauvegardes chiffrées.

### 3.4 Interface
- Design system **« Balise »** (signalétique de chantier), validé : voir [`docs/design-system.md`](docs/design-system.md).
- **Responsive, conçue d'abord pour le mobile** : parfaitement utilisable sur téléphone, tablette et ordinateur.
- Accessibilité visée : **WCAG 2.1 AA**.
- Interface **en français uniquement**.

### 3.5 Projet
- Évolutivité : le code doit pouvoir accueillir plus tard l'application mobile, les devis et la facturation sans refonte.
- Développement sur la branche `dev`. `main` ne reçoit des changements que par une pull request, fusionnée par le propriétaire du projet.

## 4. Hors périmètre

- Application mobile native (prévue dans une phase ultérieure).
- Édition de devis (phase ultérieure).
- Facturation électronique (phase ultérieure, probablement via un service existant et conforme, à étudier).
- Rôles supplémentaires (client, administrateur, sous-traitant…) : la V1 ne gère que **chef de chantier** et **ouvrier**.
- Inscription publique.
- Notifications par e-mail ou push. Seuls les e-mails de sécurité (invitation, réinitialisation du mot de passe) font partie de la V1.
- Mode hors connexion.
- Planning, calendrier ou diagramme de Gantt.
- Messagerie ou chat en temps réel.
- Gestion des stocks, du matériel et des heures travaillées.
- Multi-entreprise (plusieurs sociétés sur la même instance).
- Langues autres que le français.

## 5. Critères d'acceptation

La V1 est acceptée quand **tous** les critères ci-dessous sont remplis. Le lot qui couvre chaque groupe de critères est indiqué entre crochets.

### 5.1 Fonctionnels
**Comptes et accès** [lot 03]
- [ ] Le premier chef peut être créé par une commande sur le serveur ; il n'existe aucune page d'inscription publique.
- [ ] Un chef peut inviter un utilisateur (ouvrier ou chef). L'invité reçoit un e-mail contenant un lien à usage unique et à durée limitée, qui lui permet de définir son mot de passe. Un lien expiré ou déjà utilisé est refusé.
- [ ] Un utilisateur peut se connecter, se déconnecter et réinitialiser son mot de passe par e-mail.
- [ ] La demande de réinitialisation donne la même réponse, que l'e-mail corresponde à un compte ou non.
- [ ] Un mot de passe ne respectant pas la politique (moins de 12 caractères, courant ou déjà fuité) est refusé avec un message clair.
- [ ] Réutiliser un refresh token déjà utilisé révoque la session concernée.

**Chantiers et cloisonnement** [lot 04]
- [ ] Un chef peut créer un chantier avec son nom, son adresse, son client, sa date de début, son échéance et son budget.
- [ ] Un chef peut modifier et archiver ses chantiers, et y affecter ou en retirer des chefs et des ouvriers.
- [ ] Un utilisateur, chef ou ouvrier, ne voit **que** les chantiers auxquels il est rattaché. Accéder à un autre chantier par son URL ou par l'API renvoie une erreur 404.
- [ ] Un ouvrier ne peut ni créer, ni modifier, ni archiver un chantier, ni voir son budget.
- [ ] La liste des chantiers affiche, pour chacun, son pourcentage d'avancement et son échéance.

**Étapes et avancement** [lot 05]
- [ ] Un chef du chantier peut ajouter, modifier, réordonner et supprimer des étapes.
- [ ] Un ouvrier affecté peut faire passer une étape de `À faire` à `En cours`, puis à `Terminée (à valider)`.
- [ ] Seul un chef du chantier peut **valider** une étape, ou la **refuser** avec un commentaire obligatoire, ce qui la renvoie en `En cours`.
- [ ] Toute transition non autorisée est rejetée par l'API, par exemple un ouvrier qui tente de valider ou un saut d'état.
- [ ] Le pourcentage d'avancement est égal au nombre d'étapes validées divisé par le nombre total d'étapes. Il vaut 0 % s'il n'y a aucune étape.
- [ ] L'historique de chaque étape est conservé : qui a fait quel changement, et quand.
- [ ] Deux actions simultanées sur la même étape ne s'écrasent pas : la seconde est rejetée et l'utilisateur est invité à recharger.

**Notes, photos et documents** [lot 06]
- [ ] Tout utilisateur rattaché à un chantier peut y ajouter une note, affichée avec son auteur et sa date.
- [ ] Tout utilisateur rattaché peut envoyer une photo (JPEG, PNG, WebP, HEIC, 10 Mo maximum) ou un PDF (20 Mo maximum), puis le consulter et le télécharger.
- [ ] Un fichier d'un autre format, trop lourd ou à l'extension falsifiée est refusé.
- [ ] Un fichier détecté par l'antivirus (fichier de test EICAR) est refusé. Si l'antivirus est indisponible, tout envoi est refusé.
- [ ] Les photos stockées ne contiennent plus aucune métadonnée EXIF.
- [ ] Un fichier n'est accessible qu'aux utilisateurs autorisés sur son chantier, jamais par une URL publique.

**RGPD** [lot 07]
- [ ] Un utilisateur peut consulter et exporter ses données personnelles (format JSON).
- [ ] La suppression d'un compte efface ou anonymise ses données personnelles.
- [ ] La purge automatique applique les durées de conservation.
- [ ] Les pages de politique de confidentialité et de mentions légales sont accessibles.

### 5.2 Qualité [tous les lots, outillage au lot 01]
- [ ] mypy `--strict`, ruff, ESLint et `tsc` passent sans aucune erreur ni exception non justifiée.
- [ ] Les contrats import-linter (couches et indépendance des modules) passent.
- [ ] Les règles ESLint de sens des dépendances et d'usage du design system passent, et les limites de taille, de complexité et de duplication sont respectées.
- [ ] Couverture du domaine et des services : 100 %. Backend global : ≥ 95 %, lignes et branches. Frontend : ≥ 90 %.
- [ ] Score des tests de mutation sur le domaine et les services ≥ 90 %.
- [ ] Les tests Playwright couvrent les parcours complets du chef de chantier et de l'ouvrier, et passent.
- [ ] La CI est entièrement au vert.

### 5.3 Sécurité [lot 08, vérifié en continu dès le lot 01]
- [ ] pip-audit, pnpm audit, bandit, CodeQL et Trivy ne signalent **aucune** vulnérabilité de gravité moyenne ou plus.
- [ ] Un scan **OWASP ZAP** de l'application déployée ne remonte aucune alerte de gravité moyenne ou plus.
- [ ] Les en-têtes de sécurité sont présents (note A ou plus sur securityheaders.com ou un outil équivalent).
- [ ] La limitation des tentatives de connexion est vérifiée par un test.
- [ ] Aucun secret n'est présent dans le dépôt (vérification avec gitleaks).

### 5.4 Interface [lots 03 à 07, audit au lot 08]
- [ ] Toutes les pages sont utilisables sans défilement horizontal à 360 px, 768 px et 1280 px de large.
- [ ] Score d'accessibilité **Lighthouse ≥ 95** et aucune erreur critique **axe** sur les pages principales.
- [ ] Tous les textes de l'interface sont en français.

### 5.5 Déploiement [lot 09]
- [ ] L'application démarre sur le serveur Ubuntu avec une seule commande `docker compose up -d`.
- [ ] Elle est servie en HTTPS, et le HTTP redirige vers le HTTPS.
- [ ] Les migrations Alembic s'appliquent automatiquement et sans perte de données.
- [ ] Les sauvegardes de la base et des fichiers sont automatiques, chiffrées, avec une copie hors du domicile, et une **restauration a été testée** avec succès.
- [ ] Un README décrit l'installation, la configuration et la restauration.
