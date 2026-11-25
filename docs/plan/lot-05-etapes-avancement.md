# Lot 05 – Étapes et avancement

**Dépend de** : 04 · **Statut** : à faire · **Issue** : #5 · Peut se mener **en parallèle du lot 06**.

## Objectif
Le cœur métier : des étapes qui suivent un cycle de validation contrôlé, avec leur historique, et l'avancement calculé du chantier.

## Déjà livré par le squelette
- **Livré** (S2, S4, S5, S6, puis S11 et S12 prévus) : table des transitions, historique écrit dans la même transaction, avancement calculé, verrou de version, plafond de transitions, tableau de bord, ajout, modification, réordonnancement et suppression des étapes (S11), historique affiché (S12). La règle de suppression d'une étape validée est tranchée au lot S11.
- **Reste** : les droits selon l'affectation (ouvrier affecté, chef du chantier), l'écriture des validations dans `JournalAudit`, et les écrans de la maquette encore absents.

## Prérequis et points à trancher au démarrage
- **Suppression d'une étape déjà validée** : est-elle autorisée ? Elle modifie l'avancement. Proposition : on l'interdit, et seule une étape non validée peut être supprimée.

## Étapes
| # | Agent (modèle, effort) | Contenu | Règles |
|---|---|---|---|
| 1 | `dev-metier` **(Opus, très élevé)** | **Domaine** : `Etape` (titre, description, ordre, statut, `version`). **Table déclarative des transitions** (statut × action × rôle → statut d'arrivée) :<br>- ouvrier ou chef rattaché : `À faire` → `En cours` → `Terminée (à valider)` ;<br>- chef du chantier uniquement : `Terminée (à valider)` → `Validée`, ou → `En cours` (refus, avec un commentaire obligatoire) ;<br>- toute autre combinaison lève `TransitionInterdite`.<br>`HistoriqueEtape` (auteur, ancien statut, nouveau statut, date, commentaire). `Avancement` : validées / total, 0 % si aucune étape. **Cas d'usage** : `AjouterEtape`, `ModifierEtape`, `ReordonnerEtapes`, `SupprimerEtape` (chef), `DemarrerEtape`, `SignalerEtapeTerminee`, `ValiderEtape`, `RefuserEtape`, `ConsulterHistorique`, et le cas d'usage **public** `CalculerResumesEtapes(ids de chantiers)`. Les vues portent les **actions permises** de chaque étape. Validations et refus écrits dans `JournalAudit`. | 00, 01, 02 |
| 2 | `dev-donnees` (Sonnet, élevé) | `SqlEtapeRepository`, table de l'historique et migrations. **Verrou optimiste** : la colonne `version` est vérifiée à l'écriture ; un conflit lève `ConflitDeModification`. La transition et l'historique sont écrits dans le même Unit of Work. Adaptateur `ResumeEtapesDepuisEtapes` (déjà livré au lot S4, dans `app/composition/resume_etapes.py`), qui implémente le port `FournisseurResumeEtapes` de `chantiers` en appelant `CalculerResumesEtapes`. | 00, 03, 06, 07 |
| 3 | `dev-api` (Sonnet, moyen) | Routes `/api/chantiers/{id}/etapes` (liste, ajout, ordre), `/api/chantiers/{id}/etapes/{id}` (modification, suppression), puis, sur chaque étape, les actions `/demarrer`, `/signaler-terminee`, `/valider`, `/refuser` et `/historique`. Codes 409 pour `TransitionInterdite` et `ConflitDeModification`. | 00, 04 |
| 4 | `dev-frontend` (Sonnet, élevé) | Services : `useEtapes`, `useTransitionEtape`, `useHistorique`, `useGererEtapes`. Pages et composants, selon la maquette :<br>- liste des étapes du chantier, avec le bloc « À valider » rayé ;<br>- écran ouvrier mobile, avec « Ton étape en cours » et « Signaler terminée » ;<br>- écran de validation, avec Valider et Refuser, motif obligatoire ;<br>- historique ;<br>- message « Cette étape a été modifiée entre-temps, recharge la page » en cas de conflit 409. | 00, 05 |
| 5 | `dev-frontend` (Sonnet, élevé) | **e2e** à 360 et 1280 px : l'ouvrier signale une étape terminée → le chef la refuse avec un motif → l'ouvrier la signale de nouveau → le chef la valide → l'avancement de la liste et du détail est mis à jour. | 07 |

## Composants `ui` introduits
`BadgeStatut` (les 4 statuts de Balise), `LigneAValider` (bord rayé, fond `accent-soft`), `BandeauRayures`, `ListeOrdonnee`, `ChampTexteLong`, `Historique` (frise).

## Critères d'acceptation → tests
| Critère | Test qui le prouve | Couche |
|---|---|---|
| Un chef ajoute, modifie, réordonne et supprime des étapes | Tests des cas d'usage, tests des routes | Service, API |
| Un ouvrier affecté fait passer une étape de `À faire` à `En cours`, puis à `Terminée (à valider)` | `test_transitions.py` (table exhaustive), e2e | Domaine, e2e |
| Seul un chef du chantier valide ou refuse ; un refus exige un commentaire et renvoie l'étape en `En cours` | `test_transitions.py`, `test_refuser_etape.py` (commentaire vide refusé) | Domaine, service |
| Toute transition non autorisée est rejetée : 403 pour un ouvrier qui valide (ADR 0018), 409 pour un saut d'état | Table exhaustive paramétrée (toutes les combinaisons statut × action × rôle), `tests/integration/etapes/test_transitions_interdites.py` | Domaine, API |
| **Propriétés** : aucune suite d'actions n'atteint `Validée` sans l'action d'un chef ; l'avancement reste entre 0 et 100 % ; chaque transition produit exactement une entrée d'historique | `test_proprietes_machine_a_etats.py` (hypothesis, machine à états avec état) | Domaine |
| Avancement = validées / total, 0 % sans étape | `test_avancement.py` (cas limites et propriétés) | Domaine |
| La liste des chantiers affiche l'avancement réel | `tests/integration/chantiers/test_avancement_reel.py`, e2e | Données, API, e2e |
| L'historique est conservé : qui, quoi, quand ; il est écrit dans la même transaction que la transition | `test_valider_etape.py` (annulation de la transaction), `tests/contrats/test_etape_repository.py` | Service, données |
| Deux actions simultanées sur la même étape : la seconde reçoit 409, sans perte ni double historique | `tests/integration/etapes/test_verrou_optimiste.py` | Données, API |
| 100 % de couverture et au moins 90 % de score de mutation sur la machine à états et sur l'avancement | Rapports pytest-cov et mutmut de la CI | Domaine |
| `chantiers` n'importe toujours pas `etapes` | Contrat import-linter | Architecture |

## Hors lot
Planning et dates par étape, notifications.
