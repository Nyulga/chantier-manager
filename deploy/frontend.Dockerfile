# Image de production du frontend : construction Vite, puis fichiers statiques servis par Caddy.
# Construction à lancer depuis la racine du dépôt (voir compose.prod.yaml, `context: ..`).

# --- Étape 1 : construction du site (Node 24 et pnpm) --------------------------------------
FROM node:24-alpine AS construction

# La version de pnpm est celle de `packageManager` dans frontend/package.json.
RUN npm install --global pnpm@12.21.0

WORKDIR /frontend

# Les dépendances d'abord, pour profiter du cache tant que le verrou ne change pas.
COPY frontend/package.json frontend/pnpm-lock.yaml frontend/.npmrc ./
RUN pnpm install --frozen-lockfile

COPY frontend/ ./
RUN pnpm build

# --- Étape 2 : service des fichiers statiques ----------------------------------------------
FROM caddy:2-alpine

COPY deploy/frontend.Caddyfile /etc/caddy/Caddyfile
COPY --from=construction /frontend/dist /srv

# Utilisateur sans privilèges. Le port 80 reste utilisable : Docker autorise les ports
# bas aux conteneurs, et le binaire de Caddy porte la capacité d'écouter dessus.
# Caddy n'a besoin d'écrire que dans /tmp (HTTPS et API d'administration sont désactivés).
RUN adduser -S -u 10001 -H chantier
ENV XDG_DATA_HOME=/tmp XDG_CONFIG_HOME=/tmp
USER chantier

EXPOSE 80
