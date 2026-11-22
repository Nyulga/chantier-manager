# Image de production du frontend : construction Vite, puis fichiers statiques servis par Caddy.
# Construction à lancer depuis la racine du dépôt (voir compose.prod.yaml, `context: ..`).
# Les images de base sont épinglées par empreinte (digest), le tag restant en commentaire :
# voir backend.Dockerfile.

# --- Étape 1 : construction du site (Node 24 et pnpm) --------------------------------------
# node:24-alpine
FROM node@sha256:116b800c3754b440ee0aa3ed2f20f5bf3d99a554bfd9adeea09ea8017f6e85f5 AS construction

# La version de pnpm est celle de `packageManager` dans frontend/package.json.
RUN npm install --global pnpm@12.21.0

WORKDIR /frontend

# Les dépendances d'abord, pour profiter du cache tant que le verrou ne change pas.
COPY frontend/package.json frontend/pnpm-lock.yaml frontend/.npmrc ./
RUN pnpm install --frozen-lockfile

COPY frontend/ ./
RUN pnpm build

# --- Étape 2 : service des fichiers statiques ----------------------------------------------
# caddy:2-alpine
FROM caddy@sha256:4851e54a46b206517c574821bb5cc67f170d2156041e9fbc4c9193b45e84a75b

COPY deploy/frontend.Caddyfile /etc/caddy/Caddyfile
COPY --from=construction /frontend/dist /srv

# Utilisateur sans privilèges, sur le port 8080 : un port haut n'exige aucune capacité.
# L'image officielle donne au binaire de Caddy la capacité de fichier `cap_net_bind_service` ;
# avec `cap_drop: ALL` (voir compose.prod.yaml), un binaire qui porte une capacité absente de
# l'ensemble autorisé refuse de démarrer. On la retire donc, et on retire l'outil qui a servi.
# Caddy n'a besoin d'écrire que dans /tmp (HTTPS et API d'administration sont désactivés).
RUN apk add --no-cache libcap \
    && setcap -r /usr/bin/caddy \
    && apk del libcap \
    && adduser -S -u 10001 -H chantier
ENV XDG_DATA_HOME=/tmp XDG_CONFIG_HOME=/tmp
USER chantier

EXPOSE 8080
