# ADR 0012 – react-hook-form et zod pour les formulaires

- **Statut** : accepté
- **Date** : 2026-11-24 (hors lot). Le choix est fait dans `intent.md` (section frontend). Il n'est pas encore en place : les formulaires du squelette sont gérés avec `useState`.

## Contexte
L'application aura plusieurs formulaires : chantier, étape, refus avec motif, et, à partir du lot 03, connexion, invitation et mot de passe. Ils doivent :
- vérifier la saisie avant l'envoi (champ requis, format), pour le confort de l'utilisateur ;
- afficher sous chaque champ les erreurs 422 renvoyées par l'API (ADR 0008) ;
- rester accessibles (message lié au champ, `role="alert"`) et ne pas recharger tout l'écran à chaque frappe.

L'API reste la seule autorité sur les règles : la future application mobile ne passera pas par ce frontend.

## Décision
- **react-hook-form** gérera l'état des formulaires : valeurs, champs touchés, envoi en cours.
- **zod** décrira la forme attendue de la saisie : champs requis, formats, longueurs. Il ne contiendra **aucune règle métier** (règle 05).
- **Les erreurs de l'API l'emportent** : une 422 est affichée sous le champ concerné, même si zod avait accepté la saisie.
- **Pas encore installés** :
  - les deux formulaires du squelette (chantier et étape) utilisent `useState` et la validation de l'API, ce qui suffit à leur taille ;
  - les deux bibliothèques arriveront au lot 03, avec les formulaires de compte, dans la même étape que le premier formulaire qui en a besoin. Les formulaires existants seront alors migrés.

## Alternatives écartées
- **`useState` écrit à la main pour chaque formulaire** : c'est suffisant pour deux formulaires, mais l'état « touché », l'envoi et la validation seraient recodés à chaque nouveau formulaire.
- **Formik** : il est moins actif et redessine tout le formulaire à chaque frappe, ce qui est plus lent sur mobile.
- **Yup ou Valibot à la place de zod** : Yup est moins bien typé avec TypeScript strict. Valibot est plus léger mais moins répandu, et zod suffit.
- **Valider seulement côté API** : chaque faute de frappe coûterait un aller-retour réseau, ce qui est pénible sur un chantier où le réseau est faible.

## Conséquences
- **En bien** : tous les formulaires suivront le même modèle, la saisie sera vérifiée sans attendre le réseau, et les erreurs s'afficheront toujours au même endroit.
- **En mal** : deux dépendances de plus. Les règles de format existent à la fois dans zod et dans l'API : en cas de doute, c'est l'API qui fait foi, et un test d'API vérifie toujours la règle.
