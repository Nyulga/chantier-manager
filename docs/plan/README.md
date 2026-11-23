# Plan de développement de la V1

Référence : [`intent.md`](../../intent.md) · Décisions : [`docs/adr/`](../adr/README.md)

## Phase 1 : squelette (en cours)

On livre d'abord le **[squelette](squelette.md)** (lots S1, S2 et S3, puis S4 pour le tableau de bord de la maquette et S5 pour les corrections de relecture) : chantiers, étapes, validation et avancement, sans authentification et en ligne comme démonstration publique, sans mot de passe. Les lots 01 à 09 ci-dessous forment la phase 2 : chacun repart de ce que le squelette a déjà livré.

## Principe

- Les lots sont **verticaux** : chaque lot fonctionnel livre son backend, son frontend et ses tests de bout en bout. Chaque lot est donc démontrable et testé de bout en bout.
- Les lots s'exécutent dans l'ordre ci-dessous. **Un lot ne démarre que sur la demande explicite du propriétaire du projet.**
- Tout le travail se fait sur la branche `dev`. Rien n'arrive sur `main` sans une pull request fusionnée par le propriétaire.

## Lots

| Lot | Objectif | Dépend de | Statut |
|---|---|---|---|
| [01 – Socle](lot-01-socle.md) | Outillage, CI, squelette backend et frontend qui démarre | — | À faire |
| [02 – Noyau partagé](lot-02-noyau-partage.md) | Configuration, base de données, Unit of Work, erreurs, sécurité HTTP | 01 | À faire |
| [03 – Auth et utilisateurs](lot-03-auth-utilisateurs.md) | Comptes, connexion, sessions, invitations, mot de passe oublié | 02 | À faire |
| [04 – Chantiers et affectations](lot-04-chantiers-affectations.md) | Chantiers, affectations, cloisonnement | 03 | À faire |
| [05 – Étapes et avancement](lot-05-etapes-avancement.md) | Machine à états, validation, historique, avancement | 04 | À faire |
| [06 – Notes, photos, documents](lot-06-notes-photos-documents.md) | Notes et chaîne de contrôle des fichiers | 04 | À faire |
| [07 – RGPD et traces](lot-07-rgpd-traces.md) | Export, suppression, conservation, journal | 03 à 06 | À faire |
| [08 – Durcissement](lot-08-durcissement.md) | Audits de sécurité et d'accessibilité, correction des écarts | 07 | À faire |
| [09 – Production](lot-09-production.md) | Déploiement sur le serveur Ubuntu, sauvegardes, restauration | 08 | À faire |

```
01 ─► 02 ─► 03 ─► 04 ─┬─► 05 ─┐
                      └─► 06 ─┴─► 07 ─► 08 ─► 09
```

## Prérequis du poste (avant le lot 01)

- **Docker Desktop**, avec WSL 2, installé et démarré. C'est à l'utilisateur de l'installer, car il faut les droits administrateur.
- **uv** et **just**, installés avec l'accord de l'utilisateur.
- `gh` connecté au compte GitHub, `git`, `pnpm` et Node.js : déjà présents.

## Prérequis de la production (avant le lot 09)

Un nom de domaine, un DNS dynamique si l'adresse IP change, un accès à la box, un compte SMTP chez un fournisseur établi dans l'UE, un stockage dans l'UE pour la copie des sauvegardes, et un accès SSH par clé au serveur. Le détail est dans le [lot 09](lot-09-production.md).

## Contenu d'un fichier de lot

Chaque lot contient :
- son objectif ;
- les **points à trancher au démarrage** ;
- ses **étapes**, chacune avec son agent, son modèle et son effort, dans l'ordre domaine → service → données → API → frontend → e2e ;
- les **composants `ui`** qu'il introduit : uniquement ceux dont il a besoin ;
- la table **critère → test qui le prouve** ;
- ce qui est hors du lot.

Les vérificateurs `revue`, `conformite` et `securite` passent à la fin de **chaque** lot (skill `lot`, §4) : ils ne sont pas répétés dans les tableaux des lots.

Les lots **05 et 06** ne dépendent que du lot 04. Ils peuvent donc être menés en parallèle, chaque codeur travaillant dans son propre worktree.

## Avant de démarrer un lot

1. Relire `intent.md`, puis le fichier du lot.
2. Relire [`.claude/rules/00-principes.md`](../../.claude/rules/00-principes.md) et la règle de chaque couche touchée par le lot.
3. Travailler en TDD, dans l'ordre de construction défini par la règle 00 (§8).

Le déroulé complet (plan validé, sous-agents, vérifications, commits, journal, proposition de PR) est défini par le skill [`lot`](../../.claude/skills/lot/SKILL.md). Les preuves de chaque lot (sorties rouges et vertes, verdicts des vérificateurs) sont consignées dans [`journal/`](journal/README.md).

## Définition de « terminé » (commune à tous les lots)

Un lot est terminé quand :
- [ ] la CI est entièrement verte : lint, typage, contrats d'architecture (import-linter et ESLint), limites de taille et de complexité, duplication, tests, couverture, mutation et audits de sécurité ;
- [ ] le code a été relu contre chaque règle de `.claude/rules/` qui concerne les couches touchées ;
- [ ] les seuils sont atteints : 100 % sur le domaine et les services, ≥ 95 % sur le backend, ≥ 90 % sur le frontend, ≥ 90 % de score de mutation ;
- [ ] les critères d'`intent.md` §5 rattachés au lot sont cochés ;
- [ ] les pages livrées sont responsives (360, 768 et 1280 px), accessibles et en français ;
- [ ] tout nouveau choix structurant fait l'objet d'un ADR ;
- [ ] `CLAUDE.md` est à jour (commandes, conventions) ;
- [ ] le travail est commité et poussé sur `dev`, et le statut du lot est mis à jour dans ce tableau.
