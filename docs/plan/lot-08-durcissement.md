# Lot 08 – Durcissement

**Dépend de** : 07 · **Statut** : à faire

## Objectif
Vérifier l'application complète par des audits externes et corriger chaque écart avant la mise en production.

## Contenu
- **Scan dynamique OWASP ZAP** (*baseline* et scan authentifié) sur une instance proche de la production, lancée en local. Le scan est ajouté à la CI.
- **En-têtes de sécurité** : note A ou plus.
- **Revue de sécurité manuelle**, selon la checklist OWASP ASVS niveau 2 : authentification, sessions, contrôle d'accès, validation, fichiers, journalisation, configuration.
- **Accessibilité** : Lighthouse et axe sur toutes les pages principales, plus une vérification de la navigation au clavier.
- **Responsive** : vérification à 360, 768 et 1280 px sur toutes les pages (captures Playwright).
- **Performance** de base : temps de réponse de l'API et poids des pages, en rapport avec un usage en 4G sur le terrain.
- Correction de tous les écarts constatés, avec un test de non-régression pour chacun.

## Critères d'acceptation
- [ ] Les critères d'`intent.md` §5.3 et §5.4 sont tous cochés.
- [ ] Un rapport d'audit est versionné dans `docs/audits/`.

## Hors lot
Test d'intrusion par un tiers (à envisager après la V1).
