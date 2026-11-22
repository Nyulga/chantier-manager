# Lot 08 – Durcissement

**Dépend de** : 07 · **Statut** : à faire · **Issue** : #8

## Objectif
Vérifier l'application complète par des audits, puis corriger chaque écart avant la mise en production.

## Prérequis et points à trancher au démarrage
- Une instance **proche de la production** lancée en local (images de production, HTTPS local), préparée par `dev-socle`.

## Étapes
| # | Agent (modèle, effort) | Contenu | Règles |
|---|---|---|---|
| 1 | `dev-socle` (Sonnet, élevé) | Instance locale proche de la production. **OWASP ZAP** : scan *baseline* et scan authentifié (chef et ouvrier), ajoutés à la CI. Note des en-têtes de sécurité. **Lighthouse** et **axe** sur toutes les pages principales. Captures Playwright à 360, 768 et 1280 px. Mesures de performance : temps de réponse de l'API, poids des pages, chargement en 4G simulée. | 00 |
| 2 | `securite` **(Opus, très élevé)** | Revue complète selon la **checklist OWASP ASVS niveau 2** (authentification, sessions, contrôle d'accès, validation, fichiers, journalisation, configuration, données personnelles), sur tout le dépôt et tout son historique. | — |
| 3 | `revue` (Opus, élevé) et `conformite` (Sonnet, élevé) | Revue transverse de l'ensemble de l'application : cohérence entre les modules, dette, respect des règles. | — |
| 4 | Agent de la couche concernée | **Correction de chaque écart** (bloquant ou important), avec un **test de non-régression** pour chacun. Les constats mineurs deviennent des issues (`relecture` ou `securite`). | selon la couche |
| 5 | Coordinateur | Rapport d'audit `docs/audits/2026-lot-08.md` : constats, corrections, résultats avant et après. | — |

## Composants `ui` introduits
Aucun : on ne fait que corriger l'existant.

## Critères d'acceptation → tests
| Critère | Preuve | Couche |
|---|---|---|
| pip-audit, pnpm audit, bandit, CodeQL et Trivy : aucune vulnérabilité moyenne ou plus (§5.3) | Jobs de la CI | CI |
| ZAP : aucune alerte moyenne ou plus (§5.3) | Job ZAP de la CI, rapport archivé | CI |
| En-têtes de sécurité : note A ou plus (§5.3) | Rapport d'outil versionné dans `docs/audits/` | Production locale |
| Aucun secret dans le dépôt ni dans son historique (§5.3) | gitleaks en CI, rapport de `securite` | CI |
| Pages utilisables sans défilement horizontal à 360, 768 et 1280 px (§5.4) | Test Playwright qui mesure la largeur du document sur chaque page | e2e |
| Lighthouse accessibilité ≥ 95, aucune erreur critique axe, navigation au clavier complète (§5.4) | Job Lighthouse CI, axe dans Playwright, test e2e au clavier | e2e |
| Tous les textes de l'interface sont en français (§5.4) | Test qui parcourt les pages et repère les chaînes en anglais connues | e2e |
| Chaque écart corrigé a son test de non-régression | Tableau du rapport d'audit, avec le test de chaque correction | Toutes |

## Hors lot
Test d'intrusion par un tiers (à envisager après la V1).
