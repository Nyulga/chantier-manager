# Journal du lot S5 – Corrections de relecture

**Issue** : #38 · **Statut** : terminé le 2026-11-23 · **Plage** : `f75c1f2..` (clôture)

Le lot traite les constats rangés dans les issues `relecture` (#17 à #24, #29, #30 et #32), ainsi que #16 (sécurité). Il a été lancé à la demande du propriétaire (« regarde toutes les issues qui sont tag en relecture et agit dessus »).

## Décisions du propriétaire

- **Pagination** de `/api/chantiers` et **total exact** des étapes à valider : ils sont reportés au lot 04, avec le cloisonnement. En attendant, la pastille affiche « 50+ » quand la liste est coupée (en-tête `X-Liste-Tronquee`, ADR 0008).
- **Commentaire d'une transition** : il reste facultatif, sauf pour un refus, où il est obligatoire. Seule la documentation a été corrigée.
- **Seuil de duplication des tests TypeScript** : 6 %, au lieu des 2 % de la règle 00. Cette dérogation est écrite dans la règle 00 §4. Les tests répètent volontairement leur mise en place ; le seuil empêche seulement que la situation empire.
- **Règle de nouvelle tentative des requêtes** : elle reste posée hook par hook. `src/app` n'est pas ouvert à `src/api`.
- **`backend/app/cli`** : ce paquet vide est conservé. Il réserve l'emplacement de la CLI du lot 03 (création du premier chef), et les contrats import-linter le couvrent déjà.
- **Reports** :
  - les contrats sous PostgreSQL, au passage à PostgreSQL (ADR 0007) ;
  - les politiques `peut_voir_*`, au lot 04 ;
  - la couleur de la barre latérale en thème sombre : une décision de design, toujours ouverte.

  Ces points sont suivis dans l'issue #39.

## Étape 1 – Domaine et services (`0b1223a`)

- **Agent** : `dev-metier` (Opus, élevé).
- **Livré** :
  - le verrou de version (`ChangementStatut.version_attendue`, `Etape.verifier_version`) ;
  - les bornes de longueur dans le domaine (`exiger_longueur_max`) ;
  - les plafonds de liste déplacés en `application` ;
  - `ConsulterCapacites` ;
  - `TRANSITIONS` en `MappingProxyType` ;
  - `Montant` qui normalise `-0` ;
  - `PROFILS_ACCEPTES` dérivé de `Role` ;
  - des suites de contrat pour `UnitOfWork`, `Horloge`, `GenerateurId` et `FournisseurResumeEtapes` ;
  - le profil hypothesis « ci », déterministe.
- **Rouge** : tests de comportement en échec (`DID NOT RAISE ConflitVersionError`, `assert '-0.00' == '0.00'`, mutation de `TRANSITIONS` acceptée).
- **Vert** : `476 passed`, 100 % de couverture.

## Étape 2 – SQL et API (`61501b0`)

- **Agent** : `dev-donnees` (Sonnet, élevé).
- **Livré** :
  - **migration `0002`** : un index unique sur `(chantier_id, ordre)`, avec renumérotation des seuls doublons.
    - **Pourquoi pas le mode batch** : sous SQLite, avec les clés étrangères actives, il recrée la table `etapes`. Le `DROP` déclenche alors la cascade et vide `historique_etapes`. Un essai l'a montré : 0 ligne d'historique restante.
    - **Ce qui est vérifié** : sur une base 0001 remplie, l'historique est intact après `upgrade` et après `downgrade`.
  - **erreurs RFC 9457** : 404 de route et d'identifiant mal formé, 405 avec `Allow`, 503 générique ;
  - **422 par champ** (`erreurs: [{champ, message}]`), sans jamais recopier la saisie ;
  - `GET /api/moi` ;
  - `version` sur la transition ;
  - l'en-tête `X-Liste-Tronquee` ;
  - le retrait de `psycopg`, inutilisé pendant le squelette (ADR 0007 complété).
- **Rouge** :
  - champ des erreurs : `23 failed, 292 passed` (`'ValeurInvalideError' object has no attribute 'champ'`) ;
  - liste à valider : `7 failed` (`'tuple' object has no attribute 'tronquee'`) ;
  - contrats : `5 failed` (`DID NOT RAISE ConflitVersionError` sur un doublon d'ordre) ;
  - intégration : `63 failed, 57 passed`.
- **Vert** : `566 passed`, 100 % de couverture.

## Étape 3 – Écrans (`401c9af`)

- **Agent** : `dev-frontend` (Sonnet, élevé).
- **Livré** :
  - **droits** : ils viennent de `/api/moi` (`useCapacites`, `usePeutCreerChantier`). Il ne reste aucun `profil === 'chef'`. La section « À valider » n'apparaît plus du tout pour un ouvrier ;
  - **erreurs** : elles s'affichent sous chaque champ, avec `role="alert"` (classe `ErreurApi`, `donneesOuErreur`) ;
  - **transitions** : la `version` est envoyée ;
  - **robustesse** : un `ErrorBoundary` ; `PageIntrouvable` pour un 404 ;
  - **changement de profil** : `resetQueries`, l'événement `storage` et `key` sur l'`Outlet` ;
  - « 50+ » ;
  - **organisation** : `features/tableau-de-bord` ; les aides de test regroupées dans `src/test`, importables par les seuls tests ;
  - **nettoyage** : variantes inutilisées supprimées, apostrophes droites ;
  - **e2e** : `robustesse.spec.ts`.
- **Rouge** : `65 failed | 292 passed` (tests écrits avant le code). Le garde-fou `src/test` a d'abord échoué sur ses fixtures.
- **Vert** : `422 passed` (99,8 % des lignes), e2e 36 sur 36, deux fois de suite.

## Étape 4 – Outillage (`04decec`)

- **Agent** : `dev-socle` (Sonnet, élevé).
- **Livré** :
  - **jscpd** :
    - recette `just doublons`, appelée par `just verifier` et par la CI ;
    - `--fail-on-empty` ;
    - dépendance `jscpd` 5.4.3, licence MIT, binaire natif sans dépendance transitive.
  - **pre-commit** :
    - au commit : ruff, mypy, import-linter, bandit, Prettier, ESLint, tsc, fins de ligne et gitleaks ;
    - au push : tests et duplication ;
    - job CI « Hooks git ».
  - **Divers** :
    - `.editorconfig` ;
    - `just normaliser-fins-de-ligne` ;
    - `uv run --no-dev` dans Playwright.
- **Preuves** : chaque hook bloque une violation volontaire (import inutilisé, fichier de 311 lignes, `any`, faux jeton GitHub, CRLF, test en échec, fichiers copiés).

## Vérifications et corrections

- **revue** : aucun constat bloquant ; la migration, les données et les droits sont corrects. Trois constats importants :
  - le 503 masquait les erreurs de programmation, et sa cause n'était pas journalisée ;
  - le journal manquait ;
  - le seuil de 7 % n'avait pas été accordé.

  Les trois sont corrigés : 503 réservé aux vraies indisponibilités, ce journal, et seuil de 6 % accordé par le propriétaire.
- **conformite** : constats importants corrigés :
  - la dérogation est tracée ;
  - l'ADR 0008 est écrit (capacités, valeurs publiques, contrat d'erreur, liste tronquée) ;
  - l'ADR 0007 et la règle 03 sont complétés pour `psycopg` ;
  - la règle 04 décrit `valeurs_publiques.py`, et un test de parité des `Literal` est ajouté ;
  - `ResumeChantier` n'est plus dupliqué (carte de résumé dans `ui`).
- **securite** : aucun constat bloquant ni important. Les trois mineurs sont corrigés :
  - `hide_parameters=True` sur le moteur ;
  - noms de fichiers protégés dans les hooks ;
  - migration 0002 rejouable (`if_not_exists`).

  #16 est traitée en entier, budget borné compris.

- **Commits de correction** :
  - `218373b` (`dev-donnees` et `dev-socle`) :
    - **Rouge** : 503 au lieu de 500 sur une table absente ; trace contenant `[parameters: ... 'titre-confidentiel…']` ; `index … already exists` sur une migration rejouée ; la clé inventée recopiée dans `champ`.
    - **Vert** : `592 passed`, 100 % de couverture.
    - La migration `0002` a été retouchée avant toute fusion dans `main` ou tout déploiement. Aucune migration publiée n'a été modifiée.
  - `bcd2c51` (`dev-frontend`) :
    - **Livré** : carte `ResumeChantier` unique dans `ui`, alimentée par `resumerChantier` de `src/api` ; `lireIdentifiantChantier` ; nouvelle tentative posée sur tous les hooks de lecture ; `PROFILS` relié au schéma ; e2e plus robustes.
    - **Rouge** : `resumerChantier is not a function`, `PROFILS is not iterable`, 6 hooks qui ne rejouaient pas un 503.
    - **Vert** : `447 passed` (99,76 % des lignes, `src/test` exclu), e2e 36 sur 36, deux fois de suite.
    - **Duplication** : 0 % en production et 5 % sur les tests, pour un seuil de 6 %.
- **Restes connus** :
  - sous Windows, just transmet mal un nom de fichier contenant une apostrophe aux hooks. Le hook échoue alors, sans exécuter de code ;
  - au retour de PostgreSQL, il faudra ajouter les SQLSTATE 08 et 53 à la table des indisponibilités.
- **Contre-vérifications** : `revue` et `conformite` donnent toutes deux « conforme », sans constat bloquant ni important. Les constats mineurs sont dans #39.
- **Rattrapage CI** (`940ee47`, `68bee73`) : un test lisait `openapi.json`, qui n'est pas versionné, et un tri d'imports était masqué par le cache local de ruff.
- **CI** : verte sur `68bee73` (Backend, Frontend avec l'e2e, Hooks git, Sécurité).
