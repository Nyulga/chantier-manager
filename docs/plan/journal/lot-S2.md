# Journal du lot S2 – Chantiers et étapes

**Issue** : #11 · **Statut** : terminé le 2026-11-22 · **Plage** : `b5807f8..91dcad0` (historique réordonné après coup, voir `lot-S1.md` ; les identifiants cités sont ceux d'avant ce réordonnancement)

## Étape 1 – Domaine et cas d'usage

- **Agent** : `dev-metier` (Opus, élevé).
- **Livré** :
  - `shared` : erreurs `…Error`, `Acteur`, `Role`, ports `UnitOfWork`, `Horloge` et `GenerateurId`, et leurs fakes ;
  - `chantiers` : `Chantier`, `Adresse`, `Montant`, politiques et cas d'usage (créer, lister, consulter, vérifier l'existence, autoriser l'ajout d'une étape) ;
  - `etapes` : `Etape`, table déclarative des transitions, `HistoriqueEtape`, `calculer_avancement`, et les cas d'usage `AjouterEtape`, `ListerEtapes`, `ChangerStatutEtape` et `CalculerAvancements`.
- **Décisions du propriétaire en cours d'étape** :
  - suffixe `Error` imposé par ruff `N818` ;
  - entités sans `slots` pour le mapping impératif (règle 01 amendée, `e9a00a6`).
- **Tests et critères prouvés** :
  - `test_cycle.py` : matrice exhaustive des 32 combinaisons statut × action × rôle (6 autorisées, 26 interdites). Elle prouve que toute transition non autorisée est refusée, et que l'ouvrier ne peut ni valider ni refuser.
  - `test_proprietes.py` (hypothesis) :
    - aucune suite d'actions d'ouvrier n'atteint `validee` ;
    - chaque transition ajoute exactement une entrée d'historique ;
    - l'avancement reste entre 0 et 100.
  - `test_avancement.py` : 0 % sans étape, puis validées sur total.
  - `test_lire_chantiers.py` : budget à `None` pour l'ouvrier.
- **Rouge** : `106 failed, 19 passed`, puis `42 failed` pour la couche application (`NotImplementedError`).
- **Vert** : `207 passed`, 100 % sur domain et application.
- **Commit** : `b5807f8`.

## Étape 2 – Persistance SQLite, migration, API et composition root

- **Agent** : `dev-donnees` (Sonnet, élevé).
- **Livré** :
  - mapping impératif (composites `Adresse` et `Montant`, enums relus comme de vrais membres, `version_id_col`) ;
  - `SqlUnitOfWork`, avec `StaleDataError` traduite en `ConflitVersionError` ;
  - `GenerateurUuid7` ;
  - migration Alembic `0001`, appliquée au démarrage ;
  - routes `/api/chantiers`, `/api/chantiers/{id}/etapes` et `/api/etapes/{id}/transitions` ;
  - en-tête `X-Profil` obligatoire ;
  - erreurs au format RFC 9457.
- **Tests** :
  - `tests/contrats/` : même suite sur les repositories mémoire et SQL ;
  - `tests/migrations/` : `upgrade` sur base vide, `downgrade`, `alembic check` ;
  - `test_api_etapes.py::test_parcours_complet_de_la_creation_a_100_pour_cent` ;
  - un test de verrou optimiste (409).
- **Rouge** : `ModuleNotFoundError: No module named 'app.composition.mapping'`.
- **Vert** : `297 passed`, couverture de 99,91 %, 8 contrats respectés.
- **Commit** : `3f014ad`.

## Étape 3a – Composants Balise et profil courant

- **Agent** : `dev-frontend` (Sonnet, élevé).
- **Livré** :
  - les composants `Bouton`, `Champ`, `ZoneTexte`, `Formulaire`, `Carte`, `Pile`, `BarreAvancement`, `BadgeStatut` (jaune et rayures réservés à « Terminée (à valider) »), `Lien`, `Alerte` et `SelecteurProfil` ;
  - l'en-tête `X-Profil` envoyé par le client.
- **Rouge** : 14 suites en échec (`Failed to resolve import "./Alerte"`, …).
- **Vert** : `172 passed`, couverture de 100 %, un test axe par composant.
- **Commit** : `f23db44`.

## Étape 3b – Écrans et parcours de bout en bout

- **Agent** : `dev-frontend` (Sonnet, élevé).
- **Livré** :
  - les pages liste, création, détail avec ses étapes, et 404 ;
  - les hooks TanStack Query ;
  - un bouton par action permise renvoyée par l'API ;
  - le refus avec motif obligatoire.
- **Rouge** : 21 fichiers de test en échec (modules absents), plus `BarreAvancement` qui affichait « undefined / undefined ».
- **Vert** : `231 passed` (100 % des lignes, 97,89 % des branches), `pnpm build` vert, e2e `parcours.spec.ts` vert contre l'API réelle, à 360 et 1280 px.
- **Commit** : `91dcad0`.

## Corrections issues des vérifications

- `afa4919` (`dev-metier`) :
  - budget arrondi au centime (`"1E3"` donne `1000.00`) ;
  - client obligatoire ;
  - avancement calculé hors de la transaction des chantiers ;
  - `CreerChantier` sans fournisseur d'avancement ;
  - test de `CHANTIER_URL_BASE`.

  **Rouge** : `assert '1E+3' == '1000.00'`, `DID NOT RAISE ValeurInvalideError`. **Vert** : `306 passed`.
- Pas de calcul métier dans les pages : la barre n'affiche que le pourcentage de l'API (constat de `conformite`).

## Vérifications

- **revue** (Opus, backend) : aucun bug bloquant, tous les critères tenus et prouvés par des tests nommés.
- **conformite** (Sonnet, backend, `ui` et `api`) : conforme, aucun constat bloquant.
- **securite** (Opus) : aucun constat bloquant (voir `lot-S1.md`).
- **conformite** (écrans) : conforme, aucun constat bloquant. Dérogation tolérée dans le squelette : le lien « Nouveau chantier » dépend du profil, et l'API reste juge (403). Réserves dans #23.
- **revue** (écrans) : trois constats importants, corrigés dans le commit `fix(lot-S2): erreurs affichées près de l'action…` :
  - l'erreur de refus était invisible sur mobile ;
  - le formulaire de refus restait ouvert en profil ouvrier ;
  - l'écran restait périmé après un 409.

  S'y ajoute une collision de clés de cache. **Rouge** : 8 tests de comportement en échec (par exemple `expected [] to be undefined`, une seule lecture au lieu de deux après un 409). **Vert** : `236 passed`, e2e 16 sur 16. Constats mineurs dans #24.
- Les constats mineurs sont passés en issues : #13 à #16 (`securite`), #17 à #22 (`relecture`).
