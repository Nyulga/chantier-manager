# Déploiement de chantier-manager

Ce dossier contient tout ce qu'il faut pour mettre l'application en ligne avec Docker Compose :

| Fichier | Rôle |
|---|---|
| `compose.prod.yaml` | Les services `chantier-api` et `chantier-web`, le volume `chantier-donnees` et le réseau externe `vtt-prod_vtt-network`. Aucun port n'est publié sur l'hôte. |
| `backend.Dockerfile` | Image de l'API (Python 3.13, uv, utilisateur non root). |
| `frontend.Dockerfile`, `frontend.Caddyfile` | Image du site (construction Vite, puis fichiers statiques servis par Caddy, utilisateur non root). |
| `Caddyfile.extrait` | Le bloc à ajouter au Caddy du serveur : HTTPS, mot de passe d'accès, en-têtes de sécurité, aiguillage `/api` et site. |
| `compose.local.yaml`, `Caddyfile.local` | Surcharge pour tester sur un poste de développement, sans le Caddy du serveur. |

Le Caddy du serveur n'appartient pas à ce dépôt : on n'y ajoute que le bloc de `Caddyfile.extrait`.

## Tester en local

Depuis la racine du dépôt (Docker Desktop lancé) :

```bash
docker compose -f deploy/compose.prod.yaml -f deploy/compose.local.yaml up -d --build
# Le site est alors sur http://localhost:8080/ et l'API sur http://localhost:8080/api/health
docker compose -f deploy/compose.prod.yaml -f deploy/compose.local.yaml down
```

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

   Le réseau `vtt-prod_vtt-network` doit déjà exister (c'est celui du Caddy du serveur) ; sinon la commande s'arrête avec un message d'erreur.

3. **Brancher le Caddy du serveur** :
   - générer l'empreinte du mot de passe d'accès : `docker exec -it <conteneur-caddy> caddy hash-password` ;
   - ajouter au Caddyfile du serveur le bloc de `Caddyfile.extrait`, en remplaçant `<EMPREINTE_BCRYPT>` par cette empreinte. Ne la commite jamais ;
   - recharger Caddy : `docker exec <conteneur-caddy> caddy reload --config /etc/caddy/Caddyfile`.

   Le nom `chantier-ultra.ddns.net` doit pointer vers le serveur, et les ports 80 et 443 doivent être ouverts : Caddy obtient lui-même le certificat HTTPS.

4. **Mettre à jour** après un changement de code : `git pull`, puis la même commande `up -d --build`.

## Sauvegarder et restaurer la base

La base SQLite vit dans le volume Docker `chantier-donnees`. Pour une copie cohérente, on arrête l'API quelques secondes.

```bash
# Sauvegarde : une archive datée, HORS du clone git (le dépôt est public).
sudo install -d -m 700 -o "$USER" /srv/sauvegardes/chantier
docker compose -f compose.prod.yaml stop chantier-api
docker run --rm -v chantier-donnees:/donnees:ro -v /srv/sauvegardes/chantier:/sauvegarde alpine \
  tar czf /sauvegarde/chantier-donnees-$(date +%F).tgz -C /donnees .
docker compose -f compose.prod.yaml start chantier-api

# Restauration : remet le contenu d'une archive dans le volume (API arrêtée)
docker compose -f compose.prod.yaml stop chantier-api
docker run --rm -v chantier-donnees:/donnees -v /srv/sauvegardes/chantier:/sauvegarde alpine \
  sh -c "cd /donnees && tar xzf /sauvegarde/chantier-donnees-AAAA-MM-JJ.tgz && chown -R 10001 /donnees"
docker compose -f compose.prod.yaml start chantier-api
```

Une sauvegarde qu'on n'a jamais restaurée n'est pas une sauvegarde : teste la restauration au moins une fois. Copie aussi l'archive hors du serveur. La sauvegarde automatique, chiffrée, est prévue au lot de mise en ligne.
