---
paths:
  - "deploy/**"
  - ".github/**"
  - "justfile"
  - ".pre-commit-config.yaml"
---

# Règle 09 – Déploiement et outillage

Relire d'abord `00-principes.md`. Décisions liées : ADR 0010 (pnpm), 0013 (client généré), 0014 (uv et just), 0015 (déploiement du squelette), 0016 (protections de la démo publique).

**Pourquoi une règle dédiée** : une régression ici ne casse aucun test. Une image non figée, un conteneur qui tourne en administrateur ou une CI qui peut écrire dans le dépôt passent inaperçus, jusqu'au jour où ils servent à une attaque.

## Commandes et CI
- **Toute commande du projet passe par le `justfile`.** La CI et les hooks git appellent `just`, ils ne recopient pas les commandes. `just verifier` est la porte d'entrée de la CI.
- **Installations à l'identique** : `uv sync --locked` et `pnpm install --frozen-lockfile`, partout (poste, CI, images).
- **CI** :
  - droits minimaux (`permissions: contents: read`), élargis job par job seulement si c'est indispensable, avec un commentaire ;
  - chaque action GitHub est épinglée **par SHA complet**, avec sa version en commentaire ;
  - jamais de secret dans un fichier : seulement des secrets GitHub, jamais affichés dans les journaux ;
  - Dependabot met à jour les actions, les images et les dépendances.
- **Hooks git** (`.pre-commit-config.yaml`) : les contrôles rapides au commit, les tests et la duplication au push. Ils appellent les mêmes outils que `just verifier`.

## Images et conteneurs
- **Image de base épinglée par digest** (`image@sha256:…`), avec son nom et sa version en commentaire. Jamais `latest`.
- **Constructions en plusieurs étapes** : l'image finale ne contient ni compilateur, ni gestionnaire de paquets, ni sources inutiles.
- **Un utilisateur sans droits** (`USER`), jamais root.
- **Durcissement** commun à tous les services (`x-durcissement` dans `compose.prod.yaml`) : système de fichiers en lecture seule, `cap_drop: ALL`, `no-new-privileges`, limites de mémoire et de processus, journaux limités en taille, `healthcheck`.
- **Aucun port publié sur l'hôte** en production : le trafic passe par le reverse proxy, sur un réseau Docker interne dédié.
- **La copie locale** (`compose.local.yaml`, `Caddyfile.local`) reproduit les protections du proxy de production, pour que les tests et le pentest local voient la même chose.
- **Données** dans des volumes nommés. Une migration de base se fait après une sauvegarde.

## Serveur et dépôt public
- **Rien sur le serveur dans le dépôt** : ni adresse IP, ni chemin de l'hôte, ni nom d'un autre projet, ni état du pare-feu. Ces informations restent hors du dépôt.
- **Aucune commande sur le serveur sans l'accord du propriétaire**, donné pour cette action. Avant toute modification d'un fichier du serveur : sauvegarde horodatée, puis validation (`caddy validate`…), puis rechargement sans coupure.
- **Les données de production ne sont jamais touchées** sans demande explicite. Un déploiement qui migre la base vérifie avant et après que rien n'est perdu.

## Comment vérifier
- **Automatique** (CI) :
  - job « Hooks git » : les hooks tournent sur tout le dépôt ;
  - gitleaks sur tout l'historique ;
  - Trivy sur les fichiers de dépendances (`trivy fs`) et sur la configuration : Dockerfile et compose (`trivy config`, qui repère par exemple un conteneur sans `USER`) ;
  - `pip-audit` et `pnpm audit` sur les dépendances ;
  - `backend/tests/architecture/test_caddy_deploiement.py` (dans `just verifier`) : le bloc du serveur recopie `protections.caddy`, la copie locale l'importe, les fausses adresses du proxy sont celles de l'API, le site statique pose les mêmes en-têtes, et aucun port n'est publié en production (ADR 0016).
  - `just verifier-client` (dans `just verifier` et dans le job Frontend) : le client généré est à jour ;
  - `backend/tests/outils/*garde_agents*.py` (dans `just verifier`) : la garde des sous-agents (ADR 0017), sa table des droits alignée sur les fiches d'agents, et le hook de `.claude/settings.json`, qui doit finir par `|| exit 2`.
- **Par un agent** : `securite` (secrets, images, droits de la CI, dépôt public), `conformite` (cette règle), `pentest` (ce que le serveur expose vraiment).
- **Pas encore vérifié automatiquement** : l'épinglage par SHA ou par digest, le bloc `x-durcissement`, la validité de la composition (`docker compose config`) et la configuration réelle du Caddy du serveur ne sont contrôlés que par relecture.
