# ADR 0008 – Capacités de l'acteur, valeurs publiques et contrat d'erreur

- **Statut** : accepté
- **Date** : 2026-11-23 (lot S5)

## Contexte
La relecture des lots S1 à S4 (issues #17 à #24, #29, #30 et #32) a relevé quatre points :
- le frontend déduisait des droits du profil (`profil === 'chef'`) ;
- les bornes de saisie étaient recopiées entre le domaine, les schémas d'API et les colonnes ;
- les erreurs 404, 405 et 422 n'avaient pas toutes la même forme ;
- le frontend ne pouvait pas savoir que la liste « À valider » était tronquée.

## Décision

### 1. Les capacités de l'acteur viennent de l'API : `GET /api/moi`
- **Réponse** : `{role, peut_creer_chantier, peut_lister_etapes_a_valider}`.
- **Calcul** : le cas d'usage `ConsulterCapacites` évalue ces drapeaux avec les politiques du domaine. Il ne refait aucune règle.
- **Emplacement** : `ConsulterCapacites` vit dans `etapes`, le seul module qui voit les deux autres (contrat `chantiers-sans-etapes`). Il obtient le droit de créer un chantier par le port `DroitCreationChantier`. Ce port est branché sur le cas d'usage public `EvaluerCreationChantier` du module `chantiers`.
- **Frontend** : il affiche ou masque les actions d'après ces drapeaux, et ne compare plus jamais un profil. Les cas d'usage revérifient toujours les droits.
- **Évolution prévue au lot 03** : la route rejoindra le module `auth`. `ConsulterCapacites` deviendra alors un point d'extension, qui recevra une liste de fournisseurs de capacités. On l'étendra en ajoutant un fournisseur, sans modifier le cas d'usage.

### 2. Les valeurs publiques traversent `application`
- **Problème** : les bornes de saisie (longueurs maximales) et l'énumération `Role` sont définies dans le domaine. La couche `api` en a besoin pour ses schémas, mais n'a pas le droit d'importer `domain` (contrat `api-sans-domain`).
- **Fichier** : chaque module expose un fichier `application/valeurs_publiques.py`, qui republie ces valeurs, avec `__all__`.
- **Contenu limité** : ce fichier ne contient **que des constantes de saisie et des types de valeur immuables**. Il ne contient jamais d'entité, de règle ni de fonction.
- **Bénéfice** : chaque borne a une source unique, partagée par le domaine, le schéma d'API et la colonne.
- **Littéraux** : les statuts et les actions restent des `Literal` dans les schémas d'API. Un test de parité les compare aux énumérations du domaine.

### 3. Une seule forme d'erreur : RFC 9457
- **Format commun** : toute erreur, y compris un 404 de route, un 405 ou un identifiant mal formé (404), répond en `application/problem+json`. Son corps est `{type, title, status, detail}` (schéma `ProblemeReponse`).
- **Erreur 422** : elle ajoute `erreurs: [{champ, message}]`.
  - `champ` est un chemin pointé du corps (`adresse.code_postal`) ou un paramètre de requête.
  - Les messages sont fixes, et ne recopient jamais la saisie : ni la valeur envoyée, ni une clé inventée par le client.
  - Une `ValeurInvalideError` du domaine peut indiquer le champ concerné. L'objet valeur `Montant` porte ainsi le nom `budget`, car il ne sert qu'au budget du chantier. S'il sert un jour à un autre montant, c'est l'appelant (`Chantier`) qui fournira le nom du champ.
- **Erreur 503** : elle est réservée aux vraies indisponibilités de la base : verrou, fichier impossible à ouvrir, erreur d'entrée-sortie, disque plein ou connexion perdue. Une erreur de programmation reste un 500. La cause est journalisée, sans paramètres SQL (`hide_parameters`).
- **Erreur 409** : elle couvre une version périmée et un ajout d'étape simultané (violation d'unicité de l'ordre).

### 4. Une liste plafonnée le dit : `X-Liste-Tronquee`
- **Plafond** : `GET /api/etapes/a-valider` renvoie au plus 50 étapes.
- **En-tête** : il vaut `true` lorsque d'autres étapes attendent. Le frontend affiche alors « 50+ ».
- **Évolution** : le total exact et la pagination arriveront au lot 04, avec le cloisonnement.

## Alternatives écartées
- **Répéter les droits dans chaque réponse** (`actions_permises` partout) : c'est déjà le cas pour les étapes. Mais le lien « Nouveau chantier » et la section « À valider » ne sont rattachés à aucune ressource.
- **Ouvrir `api` à `domain`** pour les constantes : le contrat perdrait sa raison d'être.
- **Un corps paginé pour « À valider »** : il est prévu au lot 04. Un en-tête suffit pour le squelette, sans changer le type de la réponse.

## Conséquences
- Les règles 04 et 05 citent ce mécanisme.
- Un nouveau droit affiché par le frontend demande un nouveau drapeau dans `/api/moi`, jamais une condition dans le frontend.
