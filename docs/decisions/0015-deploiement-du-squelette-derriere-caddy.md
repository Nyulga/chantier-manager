# ADR 0015 – Déploiement du squelette : deux conteneurs derrière le Caddy existant

- **Statut** : accepté. Il s'écarte d'`intent.md` (Nginx), pendant le squelette uniquement.
- **Date** : 2026-11-24 (hors lot). Le choix est fait au lot S3 (`docs/plan/squelette.md`). Cet ADR le consigne après coup.

## Contexte
Le squelette devait être mis en ligne vite, comme démonstration publique. Le serveur fait déjà tourner un Caddy pour un autre projet : il occupe les ports 80 et 443 et gère le HTTPS. `intent.md` et le lot 09 prévoient Nginx, avec PostgreSQL, ClamAV et le SMTP, qui n'existent pas encore pendant le squelette.

## Décision
- **Deux conteneurs**, décrits dans `deploy/compose.prod.yaml` :
  - `chantier-api` : FastAPI avec un seul worker, la base SQLite dans le volume `chantier-donnees` (ADR 0007), et les migrations appliquées au démarrage ;
  - `chantier-web` : les fichiers statiques du frontend.
- **Durcissement** : les deux conteneurs tournent sans droits administrateur et ne publient aucun port sur l'hôte. Ils parlent sur un réseau Docker interne dédié.
- **Le Caddy déjà présent** joue le rôle de reverse proxy. Il gère :
  - le HTTPS (Let's Encrypt) ;
  - les en-têtes de sécurité ;
  - la limite de taille des requêtes.

  Un seul bloc est ajouté à sa configuration (`deploy/Caddyfile.extrait`). L'autre projet n'est pas touché.
- **Accès** : le site est une démonstration publique sans mot de passe (décision du propriétaire au lot S3). On n'y saisit aucune donnée réelle.
- **Limite dans le temps** : cette architecture vaut pendant le squelette. Le lot 09 reprend la cible d'`intent.md`. S'il garde Caddy au lieu de Nginx, il le consigne dans un nouvel ADR.

## Alternatives écartées
- **Installer Nginx dès le squelette** : il faudrait partager les ports 80 et 443 avec le Caddy existant, donc mettre un proxy derrière un autre proxy, ou couper l'autre projet. C'est plus de risque pour aucun gain pendant la démonstration.
- **Un seul conteneur (l'API sert aussi les fichiers statiques)** : il mélange deux rôles, et l'API servirait des fichiers qu'un serveur web sert mieux.
- **Publier les ports des conteneurs sur l'hôte** : cela exposerait l'API sans passer par le proxy, donc sans HTTPS ni en-têtes de sécurité.
- **Un hébergeur géré (PaaS)** : le serveur existe déjà, et la cible d'`intent.md` est un auto-hébergement.

## Conséquences
- **En bien** : la mise en ligne s'est faite sans coupure pour l'autre projet, le HTTPS est automatique, et le retour en arrière tient en deux commandes (`deploy/README.md`).
- **En mal** :
  - le projet dépend d'un Caddy qu'il partage : une erreur dans sa configuration touche les deux sites ;
  - la limite de taille et l'envoi des fichiers (`X-Accel-Redirect`, ADR 0004) sont décrits pour Nginx, et devront être revus au lot 09 si Caddy est gardé.
