# Lot 04 – Chantiers et affectations

**Dépend de** : 03 · **Statut** : à faire · **Issue** : #4

## Objectif
Gérer les chantiers et leurs affectations, avec un cloisonnement strict pour les chefs comme pour les ouvriers.

## Déjà livré par le squelette
- **Livré** (S2, S4, S6, puis S10 prévu) : création, liste et détail d'un chantier, budget en `Decimal` visible du seul chef, plafonds de la démo, port `FournisseurResumeEtapes`, modification avec verrou de version (S10).
- **Reste** : affectations, cloisonnement (404), archivage, référence du chantier, pagination et politiques de lecture (#39).

## Prérequis et points à trancher au démarrage
- **Format de la référence d'un chantier** (par exemple `CH-2026-014`, comme dans la maquette) : séquence annuelle, ou autre format.

## Étapes
| # | Agent (modèle, effort) | Contenu | Règles |
|---|---|---|---|
| 1 | `dev-metier` (Opus, élevé) | **Domaine** : agrégat `Chantier` (référence, nom, adresse, client, date de début, échéance, budget, statut actif ou archivé, chefs et ouvriers affectés), objets valeur `Adresse` et `Montant` (`Decimal`, EUR, jamais négatif). Invariants : l'échéance n'est pas avant la date de début ; un chantier a toujours au moins un chef ; un chantier archivé est en lecture seule. **Politiques** : `peut_voir`, `peut_modifier`, `peut_archiver`, `peut_voir_budget`, `peut_affecter`. **Cas d'usage** : `CreerChantier` (le créateur devient chef du chantier), `ModifierChantier`, `ArchiverChantier`, `ListerMesChantiers`, `ConsulterChantier`, `AffecterMembre`, `RetirerMembre`, et le cas d'usage **public** `VerifierAffectation`, utilisé par les autres modules. **Vues** : `ChantierVue`, avec les **actions permises** (`peut_modifier`, `peut_archiver`, `peut_affecter`) ; le budget n'est présent que pour un chef du chantier ; l'avancement et les compteurs d'étapes sont fournis par le port **`FournisseurResumeEtapes`** (voir la note ci-dessous). | 00, 01, 02 |
| 2 | `dev-donnees` (Sonnet, élevé) | `SqlChantierRepository`, table des affectations, migrations, contrainte `CHECK` sur le budget. Adaptateur provisoire `ResumeEtapesFixe`, qui renvoie un résumé vide ; il sera remplacé au lot 05. Branchement dans `app/composition/chantiers.py`. | 00, 03, 06, 07 |
| 3 | `dev-api` (Sonnet, moyen) | Routes `/api/chantiers` (liste et création), `/api/chantiers/{id}` (détail, modification), `/api/chantiers/{id}/archiver` et `/api/chantiers/{id}/membres`. **Deux schémas de réponse** : `ChantierPourChef` (avec le budget) et `ChantierPourOuvrier` (sans le budget). Un chantier hors du périmètre renvoie 404. | 00, 04 |
| 4 | `dev-frontend` (Sonnet, élevé) | Services : `useMesChantiers`, `useChantier`, `useCreerChantier`, `useModifierChantier`, `useArchiverChantier`, `useMembres`. Pages, selon la maquette : Mes chantiers (avancement et échéance, avec le compte à rebours J-n ou « En retard de n jours »), Créer ou modifier un chantier, Détail du chantier, Équipe. Formats de date `JJ/MM/AAAA` et de montant `18 450,00 €` dans `src/ui/format/`. Les boutons n'apparaissent que selon les actions permises. | 00, 05 |
| 5 | `dev-frontend` (Sonnet, élevé) | **e2e** à 360 et 1280 px : un chef crée un chantier et affecte un ouvrier ; l'ouvrier voit le chantier sans le budget ; un second chef ne le voit pas, même par son URL (404). | 07 |

> **Note de conception, sans dépendance circulaire** : `etapes` dépend de `chantiers` (via `VerifierAffectation`). `chantiers` ne doit donc jamais importer `etapes`. Le résumé des étapes arrive par le port `FournisseurResumeEtapes`, déclaré dans `chantiers/application`. La composition root branche son implémentation : `ResumeEtapesDepuisEtapes` (`app/composition/resume_etapes.py`), livré au lot S4.

## Composants `ui` introduits
`CarteChantier`, `BarreAvancement` (remplie en `fg`, jamais en `accent`, toujours accompagnée de son texte), `Badge`, `Grille`, `ChampDate`, `ChampMontant`, `NavigationLaterale` (ordinateur) et `BarreOnglets` (mobile), ainsi que les formats de date et de montant.

## Critères d'acceptation → tests
| Critère | Test qui le prouve | Couche |
|---|---|---|
| Un chef crée un chantier avec son nom, son adresse, son client, ses dates et son budget | `tests/application/chantiers/test_creer_chantier.py`, test d'intégration, e2e | Toutes |
| Les invariants sont respectés : dates cohérentes, au moins un chef, archivé en lecture seule | `tests/domain/chantiers/test_chantier.py` | Domaine |
| Un chef modifie et archive ses chantiers, et y affecte ou en retire des membres | Tests des cas d'usage, tests des routes | Service, API |
| Un utilisateur ne voit **que** ses chantiers ; tout autre chantier renvoie 404 par l'URL comme par l'API | `test_politiques_chantiers.py`, `tests/integration/chantiers/test_cloisonnement.py`, e2e | Domaine, API, e2e |
| Un ouvrier ne peut ni créer, ni modifier, ni archiver, ni voir le budget | Matrice des politiques, et `test_budget_absent_pour_ouvrier.py` (corps de la réponse) | Domaine, API |
| La liste affiche l'avancement et l'échéance de chaque chantier | `test_lister_mes_chantiers.py` (avec un faux `FournisseurResumeEtapes`, `ResumeEtapesFixe`), test Vitest de `CarteChantier` | Service, frontend |
| La matrice d'accès (rôle × action × rattachement × statut) est couverte à 100 %, avec un score de mutation d'au moins 90 % | `test_politiques_chantiers.py` paramétré, rapport mutmut de la CI | Domaine |
| Les montants s'affichent au format français, sans erreur d'arrondi | `src/ui/format/montant.test.ts`, propriété hypothesis sur `Montant` | Domaine, frontend |
| `chantiers` n'importe pas `etapes` | Contrat import-linter d'indépendance | Architecture |

## Hors lot
Planning, rôles client et sous-traitant, devis.
