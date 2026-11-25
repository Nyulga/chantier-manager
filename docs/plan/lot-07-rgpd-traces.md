# Lot 07 – RGPD et traces

**Dépend de** : 03, 04, 05, 06 · **Statut** : à faire · **Issue** : #7

## Objectif
Respecter les droits des personnes et les durées de conservation, et conserver durablement la trace des actions sensibles.

## Déjà livré par le squelette
- **Livré** : rien. Le squelette n'a ni comptes ni données personnelles, en dehors des adresses dans les journaux d'accès.
- **Reste** : tout le lot, plus la durée de conservation des journaux d'accès de l'API (#48).

## Prérequis et points à trancher au démarrage
- **Durées de conservation**, à fixer avec l'utilisateur. Propositions :

  | Donnée | Durée proposée |
  |---|---|
  | Chantiers archivés | 10 ans |
  | Journal d'audit | 1 an |
  | Sessions expirées | 30 jours |
  | Invitations et jetons expirés | 7 jours |
  | Fichiers d'un chantier supprimé | supprimés avec lui |

- **Contenu des mentions légales** : identité de l'éditeur et de l'hébergeur (le serveur personnel), à fournir par l'utilisateur. Aucune donnée réelle n'est commitée sans son accord.

## Étapes
| # | Agent (modèle, effort) | Contenu | Règles |
|---|---|---|---|
| 1 | `dev-metier` (Opus, élevé) | **Domaine** : `PolitiqueConservation` (durées nommées, règles de purge), et règles d'anonymisation : les notes et l'historique d'un compte supprimé sont attribués à « Utilisateur supprimé ». **Cas d'usage** : `ExporterMesDonnees` (profil, notes, fichiers envoyés avec leur liste et leurs métadonnées, historique), `SupprimerMonCompte`, `Purger`, `ConsulterJournal` (chef). Chaque module expose un cas d'usage public d'export et d'anonymisation de ses propres données ; `rgpd` les orchestre sans importer leur domaine. | 00, 01, 02 |
| 2 | `dev-donnees` (Sonnet, élevé) | `SqlJournalAudit` et sa migration. La suite de contrat existante, écrite au lot 02, est maintenant jouée aussi sur la version SQL. Implémentation de l'anonymisation et de la purge dans chaque module. CLI `purger`. | 00, 03, 06, 07 |
| 3 | `dev-api` (Sonnet, moyen) | Routes `/api/moi/donnees` (export JSON), `DELETE /api/moi` (avec confirmation du mot de passe), `/api/journal` (chef). | 00, 04 |
| 4 | `dev-frontend` (Sonnet, élevé) | Page « Mes données » (export, suppression du compte avec confirmation). Pages « Politique de confidentialité » et « Mentions légales », accessibles sans être connecté. | 00, 05 |
| 5 | Coordinateur | `docs/rgpd/registre-des-traitements.md` : finalités, données, durées, destinataires, sous-traitants (fournisseur SMTP, stockage des sauvegardes). | — |

## Composants `ui` introduits
`DialogueConfirmation` (Radix), `PageTexte` (pages légales).

## Critères d'acceptation → tests
| Critère | Test qui le prouve | Couche |
|---|---|---|
| Un utilisateur consulte et exporte ses données personnelles en JSON | `test_exporter_mes_donnees.py`, test d'intégration (structure de l'export), e2e | Service, API, e2e |
| La suppression d'un compte efface ou anonymise ses données personnelles ; aucune ne subsiste en base | `tests/integration/rgpd/test_aucune_donnee_apres_suppression.py` (parcours de toutes les tables) | Données |
| La purge applique les durées de conservation | `test_purger.py` (avec `HorlogeFixe` avancée au-delà de chaque durée) | Service, données |
| Le journal des actions sensibles est conservé en base, sans donnée sensible, et consultable par un chef | `tests/contrats/test_journal_audit.py` (SQL et mémoire), test de la route | Données, API |
| Les pages légales sont accessibles sans connexion | e2e, axe | Frontend |
| Le registre des traitements existe et couvre toutes les données collectées | Relecture par `conformite` et `securite` | Documentation |

## Hors lot
Gestion des consentements marketing (aucun traitement de ce type dans le projet).
