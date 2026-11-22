# Plan de développement de la V1

Référence : [`intent.md`](../../intent.md) · Décisions : [`docs/adr/`](../adr/README.md)

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

## Avant de démarrer un lot

1. Relire `intent.md`, puis le fichier du lot.
2. Relire [`.claude/rules/00-principes.md`](../../.claude/rules/00-principes.md) et la règle de chaque couche touchée par le lot.
3. Travailler en TDD, dans l'ordre de construction défini par la règle 00 (§8).

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
