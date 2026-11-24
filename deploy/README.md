# Déploiement de chantier-manager

Ce dossier contient tout ce qu'il faut pour mettre l'application en ligne avec Docker Compose :

| Fichier | Rôle |
|---|---|
| `compose.prod.yaml` | Les services `chantier-api` et `chantier-web`, le volume `chantier-donnees` et le réseau dédié `chantier-interne`. Aucun port n'est publié sur l'hôte. Les conteneurs sont durcis (voir plus bas). |
| `backend.Dockerfile` | Image de l'API (Python 3.13, uv, utilisateur non root, code en lecture seule). |
| `frontend.Dockerfile`, `frontend.Caddyfile` | Image du site (construction Vite, puis fichiers statiques servis par Caddy sur le port 8080, utilisateur non root). |
| `protections.caddy` | **Ce que le proxy applique** : compression, en-têtes de sécurité, documentation en 404, corps limité à 64 Ko, fausses adresses de robots envoyées à l'API, aiguillage `/api` et site. La copie locale l'importe. |
| `Caddyfile.extrait` | Le bloc à mettre dans le Caddy du serveur : le nom public, plus une copie de `protections.caddy` (le serveur n'a pas accès au dépôt). |
| `compose.local.yaml`, `Caddyfile.local` | Surcharge pour tester sur un poste de développement, sans le Caddy du serveur, avec les mêmes protections. |

Le Caddy du serveur n'appartient pas à ce dépôt : on n'y met que le bloc de `Caddyfile.extrait`.

**Une seule description des protections.** `protections.caddy` fait foi. Pour modifier une protection du proxy, on la change dans ce fichier, puis on recopie le changement dans `Caddyfile.extrait` : le test `backend/tests/architecture/test_caddy_deploiement.py` (lancé par `just verifier`) échoue si les deux divergent, si la liste des fausses adresses diffère de celle de l'API (`pieges.py`), ou si le site statique pose d'autres en-têtes que le proxy.

## Réseau et durcissement

**Réseau dédié.** `chantier-api` et `chantier-web` ne sont pas sur le réseau des autres projets du serveur : ils sont sur `chantier-interne`, créé par `compose.prod.yaml` (nom fixe). Ce réseau est `internal: true` : il est **fermé vers Internet**, car ni l'API ni le site n'ont besoin de sortir. Il faudra l'ouvrir au lot des courriels (SMTP). Le Caddy du serveur, qui appartient à l'autre projet servi par le même Caddy, rejoint ce réseau en plus du sien et garde sa propre sortie : les autres conteneurs de cet autre projet ne peuvent plus joindre l'API en contournant le Caddy.

**Conteneurs durcis**, pour les deux services :
- système de fichiers en lecture seule (`read_only`), avec `/tmp` en mémoire (`tmpfs`) ; seul le volume `/donnees` de l'API est inscriptible (base SQLite et migrations) ;
- le code `/app` appartient à root : l'utilisateur 10001 le lit sans pouvoir le modifier ; `PYTHONDONTWRITEBYTECODE=1` évite qu'il tente d'écrire des `.pyc` ;
- `cap_drop: ALL` et `no-new-privileges` ; le site écoute sur le port 8080 (port haut, aucune capacité nécessaire), et l'image retire la capacité `cap_net_bind_service` du binaire de Caddy, qui sinon refuserait de démarrer sans capacité ;
- mémoire et nombre de processus limités (`mem_limit`, `pids_limit`), journaux tournants (3 fichiers de 10 Mo).

**Images épinglées.** Les images de base sont référencées par empreinte (`@sha256:`), le tag restant en commentaire. Pour les mettre à jour à la main : `docker pull <image:tag>`, puis `docker inspect --format '{{index .RepoDigests 0}}' <image:tag>`. Dependabot propose aussi ces mises à jour chaque semaine.

## Défense en profondeur et adresse du client

Chaque maillon se protège sans compter sur celui de devant : le site statique (`frontend.Caddyfile`) et l'API posent eux-mêmes les en-têtes de sécurité et ne nomment pas leur logiciel (`--no-server-header` pour uvicorn). Le proxy les pose une seconde fois (même valeur, il remplace). Il retire aussi `Server` et `Via` : Caddy ajoute `Via: 1.1 Caddy` aux réponses qu'il relaie (constaté).

**Adresse réelle du client.** La limite de débit et le blocage des robots comptent par adresse. L'API tourne donc avec `--proxy-headers --forwarded-allow-ips "*"` (`backend.Dockerfile`) et lit l'adresse que le proxy met dans `X-Forwarded-For`. L'étoile est sûre à ces conditions :
- le port 8000 de l'API n'est publié nulle part (aucun `ports:` dans `compose.prod.yaml`, vérifié par le test d'alignement) ;
- le seul qui peut le joindre est le proxy, sur `chantier-interne` (fermé à Internet, trois membres) ;
- le proxy **remplace** `X-Forwarded-For` par l'adresse de la connexion au lieu de prolonger celui du client. C'est le comportement par défaut de `reverse_proxy` : « For these X-Forwarded-* headers, by default, the proxy will ignore their values from incoming requests, to prevent spoofing » ([documentation de Caddy](https://caddyserver.com/docs/caddyfile/directives/reverse_proxy)). Il ne faut donc **jamais** ajouter `trusted_proxies` au bloc, sauf si un autre proxy (un CDN par exemple) se place devant le Caddy du serveur : il faudrait alors y lister ses adresses, et seulement elles.

Une adresse fixe pour le proxy n'est pas possible : c'est l'autre projet, qui héberge le Caddy du serveur, qui le rattache au réseau, et Docker lui attribue son adresse.

**Un seul processus** (`--workers 1`) : le limiteur et la liste des adresses bloquées sont en mémoire (ADR 0016). Un second processus doublerait les limites.

## Tester en local

Depuis la racine du dépôt (Docker Desktop lancé) :

```bash
docker compose -f deploy/compose.prod.yaml -f deploy/compose.local.yaml up -d --build
# Le site est alors sur http://localhost:8080/ et l'API sur http://localhost:8080/api/health
docker compose -f deploy/compose.prod.yaml -f deploy/compose.local.yaml down -v
```

Le Caddy local rejoint `chantier-interne` comme le fera celui du serveur ; il reste aussi sur le réseau par défaut, indispensable pour publier le port 8080 sur le poste. `down -v` supprime aussi le volume de données de test.

La copie locale applique les mêmes protections que la démo (`protections.caddy`). Elle se joint de deux façons : `http://localhost:8080` depuis le poste, et `http://proxy-local:8080` depuis un conteneur du même réseau (le test d'intrusion local, règle 08). `compose.local.yaml` règle `CHANTIER_HOTES_ACCEPTES` pour ces deux noms ; la production n'accepte que le nom public et `127.0.0.1` (sonde de santé).

**Vérifier à la main** (depuis le poste) :

```bash
curl -si http://localhost:8080/                # en-têtes de sécurité, ni Server ni Via
curl -si http://localhost:8080/api/health      # idem
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8080/api/docs   # 404 (aussi /api/openapi.json)
curl -s -o /dev/null -w "%{http_code}\n" -H "X-Profil: chef" http://localhost:8080/api/chantiers/   # 404, sans redirection
curl -s -o /dev/null -w "%{http_code}\n" -X POST -H "X-Profil: chef" -H "Content-Type: application/json" \
     --data-binary @un-fichier-de-70-ko.json http://localhost:8080/api/chantiers   # 413
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8080/wp-admin   # 404, et l'adresse est bloquée en écriture
```

Ensuite, une écriture valide (`POST /api/chantiers`) doit répondre **403**, même avec un `X-Forwarded-For` falsifié. Le journal de l'API (`docker logs chantier-chantier-api-1`) montre l'adresse retenue pour chaque requête : jamais celle du proxy, jamais une valeur envoyée par le client. La limite de 20 écritures par minute s'applique à cette même adresse.

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

   La commande crée le réseau `chantier-interne`. Les données du volume `chantier-donnees` sont conservées d'une mise à jour à l'autre ; avant une migration de base, fais d'abord la sauvegarde décrite plus bas.

   **Ordre pour une mise à jour qui apporte les protections** : reconstruire les conteneurs d'abord (l'API refuse désormais les `Host` inconnus ; le proxy actuel transmet le nom public tel quel, donc la démo continue de répondre), puis changer le bloc du Caddy du serveur (étape 3).

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
   - **remplacer** le bloc `chantier-ultra.ddns.net` du Caddyfile du serveur par celui de `Caddyfile.extrait` (première installation : simplement l'ajouter). Le fichier est monté dans le conteneur : on le réécrit **sans changer d'inode** (`cat >`, jamais `sed -i` ni `mv`). `<Caddyfile>` est son chemin sur le serveur, `<extrait>` une copie de `Caddyfile.extrait` posée sur le serveur :

     ```bash
     cp <Caddyfile> <Caddyfile>.sauvegarde-$(date +%F-%H%M)
     # l'ancien bloc est retiré (du nom du site jusqu'à son `}` en colonne 0), le nouveau est ajouté
     awk '/^chantier-ultra\.ddns\.net[[:space:]]*\{/{saute=1} !saute{print} saute && /^\}/{saute=0}' <Caddyfile> > /tmp/Caddyfile.nouveau
     cat <extrait> >> /tmp/Caddyfile.nouveau
     cat /tmp/Caddyfile.nouveau > <Caddyfile>
     ```

   - valider : `docker exec <conteneur-caddy> caddy validate --config /etc/caddy/Caddyfile --adapter caddyfile`, et remettre la sauvegarde (`cat <sauvegarde> > <Caddyfile>`) en cas d'échec ;
   - recharger à chaud : `docker exec <conteneur-caddy> caddy reload --config /etc/caddy/Caddyfile --adapter caddyfile`.

   Vérifier ensuite depuis l'extérieur, en lecture seule (règle 08, mode demo) : les en-têtes de `/` et de `/api/health` (ni `Server` ni `Via`), `/api/docs` en 404. Ne **pas** demander `/wp-admin` depuis ton propre poste pour tester : cela bloquerait ton adresse en écriture pendant une heure.

   Si le journal de l'API affiche la même adresse pour tous les visiteurs, un autre proxy se trouve devant le Caddy du serveur : voir « Adresse réelle du client » plus haut.

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

Une sauvegarde qu'on n'a jamais restaurée n'est pas une sauvegarde : teste la restauration au moins une fois. Copie aussi l'archive hors du serveur. La sauvegarde automatique, chiffrée, est prévue en phase 2 (lot 09).
