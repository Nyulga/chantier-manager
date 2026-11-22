# Intent

## 1. Produit

### Pitch
Application simple de gestion de chantiers qui permet de suivre l'état d'avancement de chaque chantier et d'y centraliser les informations du terrain : notes, photos, documents et adresse.

### Utilisateurs et rôles
| Rôle | Ce qu'il peut faire |
|---|---|
| **Chef de chantier** | Crée et modifie les chantiers, affecte les ouvriers, définit les étapes, valide les étapes signalées comme terminées, consulte toutes les informations. |
| **Ouvrier** | Consulte les chantiers auxquels il est affecté, signale qu'une étape est terminée, ajoute des notes, des photos et des documents. |

### Fonctionnalités clés (V1)
1. **Chantiers** : créer, modifier et archiver un chantier (nom, adresse, client, date de début, **échéance**, **budget / prix**). Le budget n'est visible que par le chef de chantier.
2. **État d'avancement par étapes** : chaque chantier a une liste d'étapes qui suit ce cycle :
   `À faire` → `En cours` → `Terminée (à valider)`, signalée par l'ouvrier → `Validée` par le chef de chantier.
   Le chef peut aussi refuser une étape, qui repasse alors `En cours`, avec un commentaire.
   Le pourcentage d'avancement du chantier se calcule à partir des étapes **validées** uniquement.
3. **Notes** : ajout de notes datées et signées par leur auteur, affichées sous forme de fil.
4. **Photos et documents** : envoi de fichiers (photos, PDF, plans) rattachés à un chantier.
5. **Comptes et accès** : connexion, et chaque utilisateur ne voit que les chantiers qui le concernent.

### Périmètre de la V1
Le produit aura à terme deux parties : une **application web** et une **application mobile**.
La V1 couvre **uniquement l'application web**. L'application mobile viendra plus tard (voir Hors périmètre).

## 2. Architecture

### Principe général
Le projet est découpé en deux applications indépendantes :
- un **backend** qui expose une API REST et porte toutes les règles métier ;
- un **frontend web** qui consomme cette API.

L'application mobile prévue plus tard consommera la même API.

### Backend : architecture en couches + principes SOLID
On combine les deux approches :
- l'**architecture en 3 couches** donne la structure du code ;
- les **principes SOLID** définissent comment ces couches communiquent : chaque couche dépend d'**interfaces** et jamais d'implémentations concrètes.

| Couche | Rôle | Exemples |
|---|---|---|
| **Présentation (API)** | Reçoit les requêtes HTTP, valide les entrées et formate les réponses. Ne contient aucune logique métier. | Routes FastAPI, schémas Pydantic |
| **Service (métier)** | Règles métier : cycle de vie des étapes, droits par rôle, calcul de l'avancement. | `ChantierService`, `EtapeService` |
| **Données (accès)** | Persistance via des interfaces (*repositories*) et stockage des fichiers. | `ChantierRepository` (interface) → `SqlChantierRepository` (implémentation) |

Le **domaine** (entités `Chantier`, `Etape`, `Note`, `Document`, `Utilisateur`) est indépendant du framework web et de la base de données.

**Ce que ça permet :**
- **Changer de base de données** sans toucher au métier : il suffit d'écrire une nouvelle implémentation du repository.
- **Changer de stockage de fichiers** : une interface `FileStorage` avec une implémentation `LocalFileStorage` pour la V1, puis une implémentation S3 par exemple plus tard.
- **Tester la couche service** sans base de données, grâce à de faux repositories en mémoire.

### Choix techniques
| Élément | Choix | Raison |
|---|---|---|
| Langage backend | **Python 3.12+** | Lisible, très bon écosystème, demandé |
| Framework API | **FastAPI** | Moderne, typé, documentation OpenAPI générée automatiquement (utile pour le futur mobile) |
| Accès aux données | **SQLAlchemy 2** (ORM) | Indépendant du moteur de base de données |
| Migrations de schéma | **Alembic** | Faire évoluer le modèle de données sans perte |
| Base de données | **PostgreSQL** | Robuste et évolutive, installée facilement sur le serveur Ubuntu. Grâce à l'ORM et aux repositories, on n'est pas enfermé dedans. |
| Authentification | **JWT** (token d'accès + token de rafraîchissement) | Fonctionne aussi bien pour le web que pour le mobile |
| Frontend | **React + TypeScript (Vite)** | Standard, typé ; le même langage servira pour le mobile (React Native) |
| Stockage fichiers | **Disque local du serveur** derrière l'interface `FileStorage` | Simple pour la V1, remplaçable plus tard |

### Déploiement
- **Serveur Ubuntu personnel.**
- **Docker Compose** : conteneurs `api`, `web`, `db` (PostgreSQL), plus un volume pour les fichiers.
- **Nginx** en reverse proxy, **HTTPS** via Let's Encrypt.
- Sauvegardes régulières et chiffrées de la base de données et du dossier de fichiers, avec **au moins une copie hors du domicile**, stockée dans l'UE (en cas de panne, de vol ou d'incendie).
- Auto-hébergement à domicile : seuls les ports 80 et 443 sont redirigés depuis la box ; SSH est accessible uniquement par clé (ou via VPN) ; fail2ban est actif ; le serveur et la box reçoivent des mises à jour de sécurité automatiques.

## 3. Contraintes

### 3.1 Qualité du code
**Typage strict partout**
- Backend : annotations de type obligatoires et **mypy en mode `--strict`**, aucun `Any` implicite.
- Frontend : **TypeScript `strict: true`**, avec `noUncheckedIndexedAccess` et `exactOptionalPropertyTypes` ; `any` interdit par lint.
- Les types du frontend sont **générés automatiquement depuis le schéma OpenAPI** de l'API, pour qu'aucun décalage ne soit possible entre le front et le back.

**Lint et formatage**
- Backend : **ruff** (lint et formatage), **bandit** pour l'analyse de sécurité.
- Frontend : **ESLint** (règles strictes, `typescript-eslint` en mode strict) et **Prettier**.
- **Hooks pre-commit** : aucun commit possible si le lint, le typage ou les tests échouent.

**Tests**
| Niveau | Outils | Objectif |
|---|---|---|
| Unitaires (domaine et services) | pytest | **100 %** des lignes et des branches |
| Intégration (API et base réelle) | pytest + httpx + PostgreSQL en conteneur (testcontainers) | Toutes les routes, y compris les cas d'erreur et de refus d'accès |
| Frontend | Vitest + Testing Library | ≥ 90 % |
| Bout en bout | Playwright | Les parcours critiques de chaque rôle |
| Robustesse des tests | mutmut (tests de mutation) sur la couche service | Vérifier que les tests détectent vraiment les erreurs |

- Couverture globale du backend **≥ 95 %, lignes et branches**. La CI échoue en dessous de ce seuil.
- Développement piloté par les tests (TDD) pour les règles métier.

**Intégration continue**
Chaque push lance le lint, le typage, les tests, la couverture et l'audit des dépendances. Une seule étape au rouge bloque la fusion.

### 3.2 Sécurité (tolérance zéro)
Référentiel : **OWASP ASVS niveau 2** et **OWASP Top 10**.

**Authentification et mots de passe**
- Hachage **Argon2id**.
- Politique : **12 caractères minimum**, refus des mots de passe courants ou déjà apparus dans des fuites (liste locale), aucune limite maximale abusive.
- **Limitation des tentatives** de connexion (par IP et par compte), avec un blocage temporaire progressif.
- Token d'accès JWT de courte durée (15 min), token de rafraîchissement avec **rotation** et révocation.
- Sur le web : tokens stockés en **cookies `HttpOnly`, `Secure`, `SameSite=Strict`**, avec une protection CSRF.
- Réinitialisation du mot de passe par lien à usage unique, valable peu de temps.

**Autorisations**
- Les droits sont vérifiés **dans la couche service** à chaque opération, jamais seulement dans l'interface.
- Refus par défaut : un ouvrier n'accède qu'aux chantiers auxquels il est affecté. Des tests d'intégration vérifient chaque règle d'accès.

**Fichiers envoyés**
- Formats autorisés : **PDF, JPEG, PNG, WebP, HEIC**. Le format est vérifié par le contenu réel du fichier (*magic bytes*), pas par l'extension.
- Taille maximale : **10 Mo par photo et 20 Mo par PDF**.
- Les photos sont **réencodées côté serveur**, et leurs **métadonnées EXIF sont supprimées** (dont la position GPS).
- Les fichiers sont renommés avec un identifiant aléatoire, stockés hors du dossier public et **servis uniquement par l'API après vérification des droits**.

**Application et infrastructure**
- Validation stricte de toutes les entrées (Pydantic) et requêtes SQL paramétrées uniquement, via l'ORM.
- En-têtes de sécurité : CSP stricte, HSTS, X-Content-Type-Options, Referrer-Policy, et CORS limité au domaine de l'application.
- HTTPS obligatoire.
- Aucun secret dans le dépôt : variables d'environnement, et `.env` exclu de git.
- Audit des dépendances en CI (**pip-audit**, **npm audit**), avec mises à jour suivies par Dependabot ou Renovate.
- Journal des actions sensibles (connexions, validations, suppressions), sans aucune donnée sensible dans les logs.
- Conteneurs exécutés sans droits root ; pare-feu limité aux ports 80 et 443, plus SSH.

### 3.3 RGPD
- **Minimisation** : on ne collecte que les données nécessaires.
- Hébergement **en France** (UE), sur un serveur personnel auto-hébergé à domicile.
- Droits des personnes : **accès, rectification, export et suppression** du compte et des données.
- **Durées de conservation** définies (par exemple pour les chantiers archivés et les journaux), avec une purge automatique.
- Page **politique de confidentialité** et **mentions légales**.
- Registre des traitements tenu à jour.
- Sauvegardes chiffrées.

### 3.4 Interface
- **Responsive, conçue d'abord pour le mobile** : parfaitement utilisable sur téléphone, tablette et ordinateur.
- Accessibilité visée : **WCAG 2.1 AA**.
- Interface **en français uniquement**.

### 3.5 Projet
- Évolutivité : le code doit pouvoir accueillir plus tard l'application mobile, les devis et la facturation sans refonte.

## 4. Hors périmètre

- Application mobile native (prévue dans une phase ultérieure).
- Édition de devis (phase ultérieure).
- Facturation électronique (phase ultérieure, probablement via un service existant et conforme, à étudier).
- Rôles supplémentaires (client, administrateur, sous-traitant…) : la V1 ne gère que **chef de chantier** et **ouvrier**.
- Notifications par e-mail ou push.
- Mode hors connexion.
- Planning, calendrier ou diagramme de Gantt.
- Messagerie ou chat en temps réel.
- Gestion des stocks, du matériel et des heures travaillées.
- Multi-entreprise (plusieurs sociétés sur la même instance).
- Langues autres que le français.

## 5. Critères d'acceptation

La V1 est acceptée quand **tous** les critères ci-dessous sont remplis.

### 5.1 Fonctionnels
**Comptes et accès**
- [ ] Un utilisateur peut se connecter, se déconnecter et réinitialiser son mot de passe.
- [ ] Un mot de passe ne respectant pas la politique (moins de 12 caractères, courant ou déjà fuité) est refusé avec un message clair.
- [ ] Un ouvrier ne voit **que** les chantiers auxquels il est affecté. Accéder à un autre chantier par son URL ou par l'API renvoie une erreur 403 ou 404.
- [ ] Un ouvrier ne peut ni créer, ni modifier, ni archiver un chantier, ni voir son budget.

**Chantiers**
- [ ] Le chef de chantier peut créer un chantier avec son nom, son adresse, son client, sa date de début, son échéance et son budget.
- [ ] Le chef de chantier peut modifier et archiver un chantier, et affecter ou retirer des ouvriers.
- [ ] La liste des chantiers affiche, pour chacun, son pourcentage d'avancement et son échéance.

**Étapes et avancement**
- [ ] Le chef de chantier peut ajouter, modifier, réordonner et supprimer des étapes.
- [ ] Un ouvrier affecté peut faire passer une étape de `À faire` à `En cours`, puis à `Terminée (à valider)`.
- [ ] Seul le chef de chantier peut **valider** une étape, ou la **refuser** avec un commentaire obligatoire, ce qui la renvoie en `En cours`.
- [ ] Toute transition non autorisée est rejetée par l'API, par exemple un ouvrier qui tente de valider ou un saut d'état.
- [ ] Le pourcentage d'avancement est égal au nombre d'étapes validées divisé par le nombre total d'étapes. Il vaut 0 % s'il n'y a aucune étape.
- [ ] L'historique de chaque étape est conservé : qui a fait quel changement, et quand.

**Notes, photos et documents**
- [ ] Tout utilisateur affecté à un chantier peut y ajouter une note, affichée avec son auteur et sa date.
- [ ] Tout utilisateur affecté peut envoyer une photo (JPEG, PNG, WebP, HEIC, 10 Mo maximum) ou un PDF (20 Mo maximum), puis le consulter et le télécharger.
- [ ] Un fichier d'un autre format, trop lourd ou à l'extension falsifiée est refusé.
- [ ] Les photos stockées ne contiennent plus aucune métadonnée EXIF.
- [ ] Un fichier n'est accessible qu'aux utilisateurs autorisés sur son chantier, jamais par une URL publique.

**RGPD**
- [ ] Un utilisateur peut consulter et exporter ses données personnelles (format JSON).
- [ ] La suppression d'un compte efface ou anonymise ses données personnelles.
- [ ] Les pages de politique de confidentialité et de mentions légales sont accessibles.

### 5.2 Qualité
- [ ] mypy `--strict`, ruff, ESLint et `tsc` passent sans aucune erreur ni exception non justifiée.
- [ ] Couverture du domaine et des services : 100 %. Backend global : ≥ 95 %, lignes et branches. Frontend : ≥ 90 %.
- [ ] Score des tests de mutation sur la couche service ≥ 90 %.
- [ ] Les tests Playwright couvrent les parcours complets du chef de chantier et de l'ouvrier, et passent.
- [ ] La CI est entièrement au vert.

### 5.3 Sécurité
- [ ] pip-audit, npm audit et bandit ne signalent **aucune** vulnérabilité de gravité moyenne ou plus.
- [ ] Un scan **OWASP ZAP** de l'application déployée ne remonte aucune alerte de gravité moyenne ou plus.
- [ ] Les en-têtes de sécurité sont présents (note A ou plus sur securityheaders.com ou un outil équivalent).
- [ ] La limitation des tentatives de connexion est vérifiée par un test.
- [ ] Aucun secret n'est présent dans le dépôt (vérification avec gitleaks).

### 5.4 Interface
- [ ] Toutes les pages sont utilisables sans défilement horizontal à 360 px, 768 px et 1280 px de large.
- [ ] Score d'accessibilité **Lighthouse ≥ 95** et aucune erreur critique **axe** sur les pages principales.
- [ ] Tous les textes de l'interface sont en français.

### 5.5 Déploiement
- [ ] L'application démarre sur le serveur Ubuntu avec une seule commande `docker compose up -d`.
- [ ] Elle est servie en HTTPS, et le HTTP redirige vers le HTTPS.
- [ ] Les migrations Alembic s'appliquent automatiquement et sans perte de données.
- [ ] Les sauvegardes de la base et des fichiers sont automatiques, et une **restauration a été testée** avec succès.
- [ ] Un README décrit l'installation, la configuration et la restauration.
