# Déploiement de chantier-manager

Ce dossier contient tout ce qu'il faut pour mettre l'application en ligne avec Docker Compose :

| Fichier | Rôle |
|---|---|
| `compose.prod.yaml` | Les services `chantier-api` et `chantier-web`, le volume `chantier-donnees` et le réseau dédié `chantier-interne`. Aucun port n'est publié sur l'hôte. Les conteneurs sont durcis (voir plus bas). |
| `backend.Dockerfile` | Image de l'API (Python 3.13, uv, utilisateur non root, code en lecture seule). |
| `frontend.Dockerfile`, `frontend.Caddyfile` | Image du site (construction Vite, puis fichiers statiques servis par Caddy sur le port 8080, utilisateur non root). |
| `Caddyfile.extrait` | Le bloc à ajouter au Caddy du serveur : HTTPS, en-têtes de sécurité, limite de taille des requêtes, aiguillage `/api` et site. |
| `compose.local.yaml`, `Caddyfile.local` | Surcharge pour tester sur un poste de développement, sans le Caddy du serveur. |

Le Caddy du serveur n'appartient pas à ce dépôt : on n'y ajoute que le bloc de `Caddyfile.extrait`.

## Réseau et durcissement

**Réseau dédié.** `chantier-api` et `chantier-web` ne sont pas sur le réseau des autres projets du serveur : ils sont sur `chantier-interne`, créé par `compose.prod.yaml` (nom fixe). Ce réseau est `internal: true` : il est **fermé vers Internet**, car ni l'API ni le site n'ont besoin de sortir. Il faudra l'ouvrir au lot des courriels (SMTP). Le Caddy du serveur, qui appartient à l'autre projet servi par le même Caddy, rejoint ce réseau en plus du sien et garde sa propre sortie : les autres conteneurs de cet autre projet ne peuvent plus joindre l'API en contournant le Caddy.

**Conteneurs durcis**, pour les deux services :
- système de fichiers en lecture seule (`read_only`), avec `/tmp` en mémoire (`tmpfs`) ; seul le volume `/donnees` de l'API est inscriptible (base SQLite et migrations) ;
- le code `/app` appartient à root : l'utilisateur 10001 le lit sans pouvoir le modifier ; `PYTHONDONTWRITEBYTECODE=1` évite qu'il tente d'écrire des `.pyc` ;
- `cap_drop: ALL` et `no-new-privileges` ; le site écoute sur le port 8080 (port haut, aucune capacité nécessaire), et l'image retire la capacité `cap_net_bind_service` du binaire de Caddy, qui sinon refuserait de démarrer sans capacité ;
- mémoire et nombre de processus limités (`mem_limit`, `pids_limit`), journaux tournants (3 fichiers de 10 Mo).

**Images épinglées.** Les images de base sont référencées par empreinte (`@sha256:`), le tag restant en commentaire. Pour les mettre à jour à la main : `docker pull <image:tag>`, puis `docker inspect --format '{{index .RepoDigests 0}}' <image:tag>`. Dependabot propose aussi ces mises à jour chaque semaine.

## Tester en local

Depuis la racine du dépôt (Docker Desktop lancé) :

```bash
docker compose -f deploy/compose.prod.yaml -f deploy/compose.local.yaml up -d --build
# Le site est alors sur http://localhost:8080/ et l'API sur http://localhost:8080/api/health
docker compose -f deploy/compose.prod.yaml -f deploy/compose.local.yaml down -v
```

Le Caddy local rejoint `chantier-interne` comme le fera celui du serveur ; il reste aussi sur le réseau par défaut, indispensable pour publier le port 8080 sur le poste. `down -v` supprime aussi le volume de données de test.

## Déployer sur le serveur

Aucune de ces commandes ne s'exécute toute seule : chacune se lance à la main sur le serveur.

1. **Copier le code** sur le serveur (clone du dépôt, ou copie des dossiers `backend/`, `frontend/` et `deploy/`) :

   ```bash
   git clone https://github.com/Nyulga/chantier-manager.git && cd chantier-manager
   git checkout dev   # ou main, une fois la pull request fusionnée
   ```

2. **Construire et démarrer** les deux conteneurs, depuis le dossier `deploy/` :

   ```bash
   cd deploy
   docker compose -f compose.prod.yaml up -d --build
   docker compose -f compose.prod.yaml ps   # les deux services doivent être « healthy »
   ```

   La commande crée le réseau `chantier-interne`.

3. **Brancher le Caddy du serveur** (celui de l'autre projet servi par le même Caddy ; `<conteneur-caddy>` désigne son conteneur, que `docker ps` permet de retrouver) :
   - le rattacher au réseau `chantier-interne`, tout de suite et sans le redémarrer :

     ```bash
     docker network connect chantier-interne <conteneur-caddy>
     ```

   - rendre ce rattachement durable, sinon il disparaît quand le conteneur du proxy est recréé : dans le compose de cet autre projet, ajouter un réseau externe `chantier-interne` **au seul service du proxy** (les noms ci-dessous sont à adapter à ceux de son fichier) :

     ```yaml
     services:
       <service-proxy>:
         networks:
           - <reseau-du-proxy>    # le réseau actuel du proxy, à conserver
           - chantier-interne    # ajouté
     networks:
       chantier-interne:        # ajouté
         name: chantier-interne
         external: true
     ```

     Ce réseau doit exister avant le prochain `up` de l'autre projet (étape 2 de ce document) ; tant que le projet chantier est arrêté (`down`), il ne peut pas être supprimé car le proxy y est branché, et Docker l'indique par un avertissement sans conséquence.
   - sauvegarder le Caddyfile du serveur, puis y ajouter le bloc de `Caddyfile.extrait` **sans changer l'inode du fichier** (`cat >>`, pas `sed -i`), car il est monté dans le conteneur ;
   - valider : `docker exec <conteneur-caddy> caddy validate --config /etc/caddy/Caddyfile --adapter caddyfile`, et remettre la sauvegarde en cas d'échec ;
   - si le bloc de `chantier-ultra.ddns.net` est déjà dans le Caddyfile du serveur, remplacer sa cible `chantier-web:80` par `chantier-web:8080` (le site écoute désormais sur ce port) ;
   - recharger à chaud : `docker exec <conteneur-caddy> caddy reload --config /etc/caddy/Caddyfile --adapter caddyfile`.

   Le site est une **démonstration publique**, sans mot de passe : voir l'en-tête de `Caddyfile.extrait` pour le protéger.

   Le nom `chantier-ultra.ddns.net` doit pointer vers le serveur, et les ports 80 et 443 doivent être ouverts : Caddy obtient lui-même le certificat HTTPS.

4. **Mettre à jour** après un changement de code : `git pull`, puis la même commande `up -d --build`.

## Sauvegarder et restaurer la base

La base SQLite vit dans le volume Docker `chantier-donnees`. Pour une copie cohérente, on arrête l'API quelques secondes.

```bash
# Sauvegarde : une archive datée, HORS du clone git (le dépôt est public).
sudo install -d -m 700 -o "$USER" /srv/sauvegardes/chantier
docker compose -f compose.prod.yaml stop chantier-api
docker run --rm -v chantier-donnees:/donnees:ro -v /srv/sauvegardes/chantier:/sauvegarde alpine@sha256:f59abe656b692d901e184be3445e084786602108599d2a51d229c0f5a48c71bf \
  tar czf /sauvegarde/chantier-donnees-$(date +%F).tgz -C /donnees .
docker compose -f compose.prod.yaml start chantier-api

# Restauration : remet le contenu d'une archive dans le volume (API arrêtée)
docker compose -f compose.prod.yaml stop chantier-api
docker run --rm -v chantier-donnees:/donnees -v /srv/sauvegardes/chantier:/sauvegarde alpine@sha256:f59abe656b692d901e184be3445e084786602108599d2a51d229c0f5a48c71bf \
  sh -c "cd /donnees && tar xzf /sauvegarde/chantier-donnees-AAAA-MM-JJ.tgz && chown -R 10001 /donnees"
docker compose -f compose.prod.yaml start chantier-api
```

Une sauvegarde qu'on n'a jamais restaurée n'est pas une sauvegarde : teste la restauration au moins une fois. Copie aussi l'archive hors du serveur. La sauvegarde automatique, chiffrée, est prévue au lot de mise en ligne.
