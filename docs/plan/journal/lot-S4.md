# Journal du lot S4 – Tableau de bord

**Issue** : #28 · **Statut** : terminé le 2026-11-22 · **Plage** : `ce4485d..` (clôture)

Le lot reprend la page d'accueil de la maquette Balise (« Tableau de bord · chef ») : la barre latérale, le bloc « À valider », les cartes de chantier enrichies et le fil d'activité récente.

## Décisions du propriétaire

- **Périmètre** : le tableau de bord complet, activité récente comprise.
- **Éléments non câblés** : « Équipe », « Inviter un utilisateur » et la recherche sont affichés comme sur la maquette, mais **désactivés, avec la mention « Bientôt »**. Ce ne sont pas des liens morts. Ils seront câblés au lot 03, avec les comptes.
- **Pas de comptes** : « Signalée par K. Benali » devient « Signalée le … ». L'activité dit « Le chef », « L'ouvrier » ou « Tu ». Le code de référence du chantier (`CH-2026-…`) n'est pas affiché, car il n'existe pas dans les données.
- **Code partagé du frontend** : il va dans `src/api` (ADR 0006, règle 05 ajustée).
- **Issues #13, #14 et #15** : traitées pendant S4 **à la demande du propriétaire** (« corrige l'issue… », puis « lance la correction des erreurs qu'il y a dans les issues »), en gardant en ligne l'autre projet servi par le même Caddy, avec un réseau dédié. Elles étaient prévues pour la phase 2.
- **Base SQLite** : décision du squelette, consignée dans l'ADR 0007 à la demande de l'audit global.
- **« Examiner » et « Valider »** sur chaque ligne « À valider » : c'est ce que montre la maquette du tableau de bord. « Refuser » se fait depuis le détail du chantier, qui demande le motif obligatoire.
- **Historique git** : les détails du serveur publiés avant S4 restent dans l'historique. Ils ne contiennent aucun secret, et l'historique n'est pas réécrit.

## Étape 1 – Domaine et services (`02b468d`)

- **Agent** : `dev-metier` (Opus, élevé).
- **Livré** :
  - l'objet valeur `Delai` et `calculer_delai` ;
  - le port `FournisseurResumeEtapes`, qui remplace `FournisseurAvancement` ;
  - `ResumeEtapes` (validées, total, à valider) ;
  - `Etape.signalee_le()` et `trier_par_signalement` ;
  - les cas d'usage `CalculerResumesEtapes`, `ListerEtapesAValider` (réservé au chef) et `ListerActiviteRecente` (limite de 1 à 50, 10 par défaut).
- **Rouge** : `50 failed, 198 passed`, sur des comportements (`DID NOT RAISE ValeurInvalideError`, `assert {(0, False)} == {(3, True)}`, …).
- **Vert** : `363 passed`, 100 % sur domain et application.

## Étape 2 – SQL et API (`57c6994`)

- **Agent** : `dev-donnees` (Sonnet, élevé).
- **Livré** :
  - les requêtes SQL, sans N+1 (2 requêtes par lecture) ;
  - les routes `GET /api/etapes/a-valider` (403 pour un ouvrier) et `GET /api/activite?limite=N` (422 hors bornes) ;
  - les nouveaux champs de `ChantierReponse` : compteurs, `jours_restants` et `en_retard` ;
  - le client régénéré.
- **Rouge** : contrat `9 failed` (`NotImplementedError` côté SQL), API `19 failed` (404 et `KeyError`).
- **Vert** : `397 passed`, couverture de 99,93 %.

## Étape 3 – Frontend (`9d40eac`)

- **Agent** : `dev-frontend` (Sonnet, élevé).
- **Livré** :
  - les composants Balise : barre latérale, navigation (active ou « Bientôt »), bandeau à rayures, pastille, puce de chantier, avatar, fil d'activité, bloc et ligne « À valider » ;
  - `PageTableauDeBord` sur `/`, et la liste des chantiers déplacée sur `/chantiers` ;
  - l'e2e `tableau-de-bord.spec.ts`.
- **Dépendance ajoutée** : `@axe-core/playwright` 4.14.0, en développement seulement. Elle sert à vérifier les contrastes dans un vrai navigateur. C'est un paquet officiel de Deque, sous licence MPL-2.0.
- **Rouge** : 23 tests de page et 18 fichiers `ui` en échec (modules absents, comportement de `Lien`).
- **Vert** : `348 passed` (100 % des lignes), e2e 24 sur 24 à 360 et 1280 px.

## Vérifications et corrections

- **revue** : 4 constats importants, tous corrigés.
  - Délai calculé en UTC : `4008609` le calcule à la date de Paris (`Horloge.aujourd_hui()`, `tzdata`). Le test « 23:30 UTC donne le lendemain » couvre l'hiver et l'été.
  - Message 409 perdu, focus perdu et e2e fragile : corrigés dans `1e9bcb5`. L'alerte est au niveau de la section, le focus passe à la ligne suivante, l'e2e utilise des noms uniques et vérifie les 100 % sur le détail du chantier.
- **conformite** : constats importants corrigés.
  - Le libellé est maintenant « Tu as validé ».
  - La ligne à valider a le bord rayé et le fond `accent-soft`.
  - Le droit « À valider » est décidé par l'API : un 403 masque la section.
  - L'ADR 0006 est écrit.
  - Les mineurs sont corrigés : la politique `peut_consulter_activite`, `ResumeEtapesChantier`, les tokens `--container-*`, et les tests sans boucle.
- **securite** : aucun constat bloquant.
  - Le nom de l'autre projet est retiré de `deploy/` (`ef7b6bf`).
  - Le réseau `chantier-interne` est en `internal: true`.
  - Les SHA de la CI ont été revérifiés un par un.
  - gitleaks échoue s'il n'analyse aucun commit.
  - La liste « À valider » est plafonnée à 50 en SQL (`19bd07b`).
- **Issues #13, #14 et #15** (réseau dédié, durcissement, épinglage et analyses de sécurité en CI) : livrées dans la même période (`67fc5b6`). Le serveur reste à basculer au déploiement.
- **CI** : verte sur `1e9bcb5` (backend, frontend avec l'e2e, et sécurité).

## Restes connus

- La barre latérale devient claire en thème sombre, car Balise ne définit pas de barre sombre. C'est une décision de design à prendre.
- La transition n'envoie pas la `version` de l'étape : le 409 vient de l'état de l'étape. À traiter au lot 05.
- Un ouvrier voit brièvement « Chargement… » avant que le 403 ne masque la section.
- Il n'y a pas d'index sur `etapes.statut` ni sur `historique_etapes.date`. C'est négligeable à l'échelle du squelette.
