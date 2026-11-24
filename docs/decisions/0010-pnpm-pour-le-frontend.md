# ADR 0010 – pnpm pour les dépendances du frontend

- **Statut** : accepté
- **Date** : 2026-11-24 (hors lot). Le choix est fait depuis le lot S1 (`intent.md`, section outils). Cet ADR le consigne après coup.

## Contexte
Le frontend dépend de nombreux paquets npm. Il faut :
- des installations identiques sur le poste Windows, dans la CI et dans l'image Docker ;
- des installations rapides en CI ;
- éviter qu'un paquet utilise une dépendance qu'il n'a pas déclarée.

## Décision
- **Outil** : pnpm installe les dépendances du frontend.
- **Version fixe** : la version est figée dans le champ `packageManager` de `frontend/package.json`. La CI la lit à cet endroit (`pnpm/action-setup`).
- **Installation à l'identique** : elle se fait toujours avec `pnpm install --frozen-lockfile`, via `just installer`, la CI et le Dockerfile. Si `pnpm-lock.yaml` ne correspond pas à `package.json`, l'installation échoue au lieu de se mettre à jour en silence.
- **Audit** : `pnpm audit` tourne en CI (`intent.md`, section 3.2).

## Alternatives écartées
- **npm** : il est fourni avec Node, mais il est plus lent. Son dossier `node_modules` est « aplati », ce qui permet d'utiliser une dépendance non déclarée sans le voir.
- **Yarn** : il est aussi rapide, mais ses versions récentes changent le fonctionnement habituel (Plug'n'Play), ce qui gêne certains outils. Il n'apporte rien de plus que pnpm ici.
- **Bun** : il est très rapide, mais il est plus récent et moins bien pris en charge par les outils de sécurité et par Dependabot.

## Conséquences
- **En bien** : les installations sont rapides et identiques partout, et une dépendance oubliée dans `package.json` fait échouer l'installation au lieu de passer inaperçue.
- **En mal** : il faut installer pnpm sur le poste (via Corepack ou winget). Un contributeur qui lance `npm install` par erreur crée un second fichier de verrouillage, qu'il faut supprimer.
