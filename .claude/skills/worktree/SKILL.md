---
name: worktree
description: Crée, liste et range les worktrees Git de chantier-manager dans .claude/worktrees/, pour isoler une grosse tâche ou faire travailler plusieurs agents codeurs en parallèle sans collision. Utiliser quand l'utilisateur tape « /worktree », veut « travailler à part » sur une fonctionnalité, voir ses worktrees ou en ranger un, ou quand le skill lot mène deux étapes indépendantes en parallèle.
argument-hint: "[creer <type>/<nom> | lister | ranger <nom>]"
---

# worktree · des dossiers de travail séparés

Leçon MH-10. Un worktree est un second dossier de travail du même dépôt, avec ses fichiers et sa branche : un agent par worktree, et aucun n'écrase le travail d'un autre.

**Pourquoi un skill et pas un sous-agent** : la garde des sous-agents (ADR 0017) leur interdit de modifier Git, et le hook `commit_sur_dev.py` n'accepte les commits que sur `dev`. C'est donc **la session principale** (le coordinateur) qui crée, liste et range les worktrees. Les agents codeurs y travaillent **sans commiter** ; le coordinateur intègre ensuite leurs changements sur `dev`, où il commite comme d'habitude.

Tout se passe dans `.claude/worktrees/`, ignoré par Git.

## Créer `<type>/<nom>`
1. **Le `.gitignore`** : `git check-ignore -q .claude/worktrees/x` doit répondre. Sinon, s'arrêter et le signaler.
2. **Le point de départ** : `git fetch origin`, puis partir de la branche **locale** `dev` (elle porte le travail pas encore poussé). Si `origin/dev` est en avance, le signaler et demander avant de continuer. Toujours dire de quelle branche on part.
3. **La création** : `git worktree add .claude/worktrees/<nom> -b <type>/<nom> dev`. Un nom ou une branche qui existe déjà : demander s'il faut le reprendre ou en choisir un autre.
4. **Les fichiers locaux** : un worktree neuf n'a aucun fichier ignoré par Git. Copier ceux que liste `.worktreeinclude` (à la racine, syntaxe du `.gitignore`), en recréant leurs dossiers, s'ils existent. Donner **les noms** des fichiers copiés, jamais leur contenu, et prévenir : ces copies visent la même base et le même port que le dossier principal.
5. **Les dépendances**, dans le worktree : `just installer` (`uv sync --locked`, puis `pnpm install --frozen-lockfile`).
6. **Les tests de départ** : `just verifier` dans le worktree. S'ils échouent, donner les échecs, demander s'il faut continuer, et ne rien supprimer.
7. **Le compte rendu** : chemin, branche et point de départ, fichiers copiés, dépendances, résultat des tests.

## Faire travailler un agent codeur dans le worktree
- Lui donner le chemin du worktree comme dossier de travail, en plus de sa consigne habituelle (skill `lot`).
- Il ne commite pas (ADR 0017). Le coordinateur relit le résultat : `git -C .claude/worktrees/<nom> status` et `git -C .claude/worktrees/<nom> diff`.

## Intégrer sur `dev`
1. Depuis le dossier principal, sur `dev` : appliquer les changements du worktree (`git -C .claude/worktrees/<nom> diff dev | git apply --index`, ou copie des fichiers créés), puis `just verifier`.
2. Commiter sur `dev` selon le skill `git-conventional`, puis ranger le worktree.
3. Deux worktrees qui ont touché le même fichier : s'arrêter et demander à l'utilisateur ; on n'écrase jamais un changement par un autre.

## Lister
`git worktree list` : pour chacun, le chemin, la branche et le commit abrégé.

## Ranger `<nom>`
- `git worktree remove .claude/worktrees/<nom>`, puis `git branch -d <type>/<nom>`.
- **Jamais `rm -rf`** sur un worktree.
- Des modifications non intégrées, ou une branche non fusionnée : le dire, et demander l'accord de l'utilisateur avant `--force` ou `-D`.

## Types de branche
`feature`, `fix`, `refactor`, `chore`. Pour un autre besoin, proposer le plus proche et demander.

## Règles
- Deux tâches qui touchent les mêmes fichiers restent l'une après l'autre (skill `lot`, §3).
- On ne fusionne rien dans `main`, on ne pousse aucune branche de worktree.
- `bgIsolation` reste à sa valeur par défaut : une session en arrière-plan doit entrer dans un worktree pour modifier un fichier suivi.
