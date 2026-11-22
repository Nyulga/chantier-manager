---
name: lot
description: Traiter un lot de docs/plan/ selon le process du projet chantier-manager. La session principale coordonne, des sous-agents codent couche par couche en TDD, des sous-agents vérifient, puis la PR est proposée. Utiliser quand l'utilisateur tape « /lot N » ou demande de traiter un lot.
---

# lot · notre façon de développer un lot

Ce skill définit le process du projet. Il s'applique à chaque lot, sans qu'on ait besoin de le redire.
Argument : le numéro du lot (`$ARGUMENTS`), par exemple `03`.

## Rôles

- **Coordinateur = la session principale**, en **Opus 5.5, effort élevé** au minimum. Si la session tourne sur un autre modèle, s'arrêter et demander à l'utilisateur de faire `/model`. Un sous-agent ne peut pas lancer d'autres sous-agents : le coordinateur ne doit donc jamais être lui-même un sous-agent.
- Le coordinateur **ne code pas les couches lui-même**. Il planifie, délègue, contrôle, commite et rend compte. Il peut faire seul une correction triviale : une faute de frappe, ou un import oublié signalé par le lint.
- **Seul le coordinateur commite et pousse**, toujours sur `dev`. Les sous-agents ne font jamais de commit, de push, de checkout ni de reset.

### Sous-agents, modèle et effort

| Agent | Couche ou rôle | Modèle | Effort | Pourquoi |
|---|---|---|---|---|
| `dev-metier` | `domain` et `application` | Opus | élevé | Règles métier, machine à états, droits : le cœur, où une erreur coûte le plus cher |
| `dev-donnees` | `infrastructure`, migrations, composition root | Sonnet | élevé | Adaptateurs bien cadrés par les ports et les tests de contrat |
| `dev-api` | `api` | Sonnet | moyen | Couche mince et très encadrée (règle 04) |
| `dev-frontend` | `frontend` | Sonnet | élevé | Design system, accessibilité, responsive |
| `dev-socle` | Outillage, CI, Docker, Nginx, serveur | Sonnet | élevé | Configuration précise, mais sans logique métier |
| `revue` | Vérification : critères, correction, tests | Opus | élevé | Doit trouver ce que les codeurs ont raté |
| `conformite` | Vérification : règles `.claude/rules/`, design system, commentaires | Sonnet | élevé | Contrôle systématique, liste de points précise |
| `securite` | Vérification : sécurité (ASVS niveau 2), secrets, RGPD | Opus | élevé | Tolérance zéro |
| `backlog` | Issues GitHub | Sonnet | faible | Tâche simple et mécanique |

**Ajustements imposés** : le coordinateur les passe dans les paramètres `model` et `effort` de l'outil Agent.
- **Lot 03** (sessions, tokens, mots de passe) et **lot 06** (chaîne de contrôle des fichiers, ClamAV) : `dev-donnees` passe en **Opus, effort élevé**.
- **Lot 05** (machine à états, avancement) : `dev-metier` passe en **effort très élevé (`xhigh`)**.
- **Lot 08** (durcissement) : `securite` passe en **effort très élevé (`xhigh`)**.
- **Lot 09** (production) : `dev-socle` passe en **Opus, effort élevé**.

## 1. Préparer

1. `git checkout dev && git pull origin dev`. Si `main` a reçu des changements, `git merge origin/main`.
2. Lire, dans l'ordre :
   - `intent.md` ;
   - `docs/plan/README.md`, puis `docs/plan/lot-$ARGUMENTS-*.md` ;
   - les ADR concernés ;
   - `.claude/rules/00-principes.md` et la règle de chaque couche touchée.
3. Vérifier que les lots dont il dépend sont « Terminé » dans `docs/plan/README.md`. Sinon, s'arrêter.
4. Vérifier les outils nécessaires : `gh`, `git`, `uv`, `pnpm`, `just`, `docker` (avec le démon lancé). S'il en manque un, s'arrêter et le dire.
5. Retrouver l'issue du lot : `gh issue list --label lot --search "Lot $ARGUMENTS"`.
6. Noter le commit de départ, `git rev-parse HEAD`. Il servira de base aux vérifications.

## 2. Planifier, puis attendre la validation

Présenter à l'utilisateur :
- les **étapes**, dans l'ordre de construction de la règle 00 (§8) : domaine → service → données → API → frontend → bout en bout ;
- pour chaque étape : l'agent qui s'en charge, avec son modèle et son effort, les fichiers prévus et la règle qui s'applique ;
- pour **chaque critère d'acceptation** du lot : le ou les tests qui le prouveront, et la couche testée ;
- les critères flous ou impossibles à tester, et les questions ouvertes.

**STOP : attendre la validation explicite du plan par l'utilisateur avant de lancer le moindre agent.**

## 3. Exécuter, étape par étape, en TDD

Pour chaque étape du plan :
1. **Lancer l'agent codeur.** Lui donner :
   - le numéro du lot et l'étape ;
   - les critères visés et la liste des tests attendus ;
   - les fichiers concernés ;
   - ce que les étapes précédentes ont livré : ports, vues, routes et schémas OpenAPI.

   L'agent écrit d'abord les tests, les **voit échouer**, écrit le code, puis les voit passer. Il rend la sortie rouge et la sortie verte.
2. **Contrôler** soi-même :
   - lancer `just verifier` ;
   - vérifier que la sortie rouge existe et qu'elle échoue **pour la bonne raison** (pas une erreur d'import ou de syntaxe) ;
   - si la vérification échoue, renvoyer le travail au même agent, avec la sortie d'erreur.
3. **Commiter** sur `dev`, avec le message `feat(lot-$ARGUMENTS): <étape>` (par exemple `feat(lot-03): domaine utilisateur et politique de mot de passe`), puis `Refs #<issue>`. Pousser sur `origin/dev`.
4. **Compléter le journal** du lot, `docs/plan/journal/lot-$ARGUMENTS.md` : l'étape, l'agent utilisé, les tests ajoutés, un extrait des sorties rouge et verte, et le commit.

Les étapes s'enchaînent **une par une**, parce que chacune s'appuie sur la précédente. On ne parallélise que des étapes indépendantes et sans fichier commun, par exemple les lots 05 et 06 s'ils sont menés ensemble. Dans ce cas, chaque agent codeur travaille dans son propre worktree (`isolation: "worktree"`), et le coordinateur intègre les résultats.

## 4. Vérifier

1. Lancer **en parallèle** `revue`, `conformite` et `securite`, sur la plage `<commit de départ>..HEAD`.
2. Pour chaque constat `bloquant` ou `important` :
   - le faire corriger par l'agent de la couche concernée ;
   - commiter `fix(lot-$ARGUMENTS): <ce qui est corrigé>` ;
   - relancer uniquement le vérificateur concerné.
3. Après **deux allers-retours** sans résolution, s'arrêter et soumettre le problème à l'utilisateur.
4. Les constats `mineur` et hors lot ne sont pas corrigés dans le lot : ils deviennent des issues, via l'agent `backlog` (label `relecture`).
5. **CI** : suivre `gh run watch` sur le dernier push. La CI doit être entièrement verte, y compris les tests de mutation, qui ne tournent qu'en CI Linux.

## 5. Clore le lot et proposer la PR

1. Vérifier la **définition de « terminé »** de `docs/plan/README.md`, point par point.
2. Cocher les critères dans le fichier du lot et dans `intent.md` §5. Passer le statut du lot à « Terminé ». Mettre `CLAUDE.md` à jour si des commandes ou des conventions ont changé. Commit : `docs(lot-$ARGUMENTS): clôture du lot`.
3. Faire le bilan à l'utilisateur :
   - les critères, avec le test qui prouve chacun ;
   - les verdicts des trois vérificateurs ;
   - le lien de la CI ;
   - les issues créées.
4. **Proposer** la PR de `dev` vers `main`, **sans l'ouvrir**. Ne l'ouvrir (`gh pr create --base main --head dev`) que si l'utilisateur dit oui. Le corps de la PR contient :
   - les critères cochés, avec leurs tests ;
   - les sorties rouge et verte, tirées du journal ;
   - `Closes #<issue>`.
5. **Ne jamais fusionner** : la fusion appartient à l'utilisateur.

## Nomenclature des commits
- `feat(lot-N): <étape>` : une étape d'un lot.
- `fix(lot-N): <ce qui est corrigé>` : une correction.
- `chore: <quoi>` : mise en place, outillage hors lot.
- `docs: <quoi>` ou `docs(lot-N): <quoi>` : documentation.

Le message est en français et ne contient aucun secret. Il se termine par la ligne d'attribution demandée par la session.

## Commandes de référence (créées au lot 01)
| Commande | Rôle |
|---|---|
| `just verifier` | lint, formatage, typage, contrats d'architecture, limites de taille, tests backend et frontend avec leurs seuils |
| `just test-back <chemin ou -k nom>` | un test ou un groupe de tests backend |
| `just test-front <motif>` | un test ou un groupe de tests frontend |
| `just e2e` | tests Playwright |
| `just client` | régénère le client API depuis OpenAPI |

Au lot 01, ces commandes n'existent pas encore : c'est `dev-socle` qui les crée, et le coordinateur vérifie leur fonctionnement avec les outils installés à ce moment-là.

## Règles
- Ne pas sortir du lot. Une idée hors lot est signalée, puis transformée en issue ; elle n'est jamais codée.
- Ne jamais toucher à `main`.
- En cas de contradiction entre ce skill et `intent.md`, `intent.md` prévaut : le signaler à l'utilisateur.
