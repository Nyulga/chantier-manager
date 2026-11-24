# ADR 0009 – TanStack Query pour les données venant de l'API

- **Statut** : accepté
- **Date** : 2026-11-24 (hors lot). Le choix est fait depuis le lot S1 (`intent.md`, section frontend). Cet ADR le consigne après coup.

## Contexte
Le frontend affiche surtout des données qui viennent de l'API : chantiers, étapes, capacités de l'acteur, activité. Il doit :
- les mettre en cache, pour ne pas recharger un écran déjà vu ;
- les rafraîchir après une action (une étape validée change l'avancement et la liste « À valider ») ;
- rejouer une requête après une panne, mais pas après un refus (403, 404, 422) ;
- montrer le chargement et les erreurs de façon uniforme.

Aucune règle métier ne doit vivre dans le frontend : la future application mobile utilisera la même API.

## Décision
- **Bibliothèque** : TanStack Query gère toutes les données venant de l'API.
- **Hooks** : les appels passent par des hooks `use…` du dossier `services` de chaque fonctionnalité. Ce sont les seuls à appeler `src/api` (règle 05).
- **Partagé dans `src/api`** (ADR 0006) : les clés de cache, les invalidations et l'erreur `ErreurApi`. Cette erreur est déclarée comme type d'erreur par défaut de la bibliothèque.
- **Nouvelle tentative** : la règle `reessayerRequete` ne rejoue jamais un refus de l'API. Elle est posée sur chaque hook de lecture (décision du lot S5).
- **Client** : un seul client, créé dans `src/app/providers.tsx`.
- **Pas de store global** : l'état local reste dans les composants (ADR 0005).

## Alternatives écartées
- **`fetch` et `useEffect` écrits à la main** : il faudrait recoder le cache, l'invalidation, les nouvelles tentatives et l'annulation dans chaque écran. Le résultat serait du code répété et des cas limites oubliés.
- **Redux ou Zustand** : ils sont faits pour l'état de l'interface, pas pour celui du serveur. Il faudrait écrire soi-même le chargement et le rafraîchissement. Un store global est déjà écarté par l'ADR 0005.
- **RTK Query** : il fait le même travail, mais impose Redux en plus, alors que le projet n'en a pas besoin.
- **SWR** : il est plus léger, mais moins complet pour les mutations, l'invalidation ciblée et les nouvelles tentatives au cas par cas, dont l'écran « À valider » a besoin.
- **Chargement par les routes (loaders de React Router)** : il lie les données à la navigation. Un même bloc, comme les capacités ou la pastille « À valider », sert pourtant sur plusieurs pages.

## Conséquences
- **En bien** : le cache, le rafraîchissement après une action et les états de chargement sont uniformes, et un écran n'appelle jamais l'API directement.
- **En mal** : c'est une dépendance de plus, à suivre lors de ses montées de version. Ses réglages par défaut ne conviennent pas toujours : par exemple, elle rejoue une requête même après un 403. Il faut donc les surcharger, et un hook qui l'oublie retombe sur ce défaut.
- Un nouvel écran qui lit l'API ajoute un hook dans `services`, jamais un appel dans un composant.
