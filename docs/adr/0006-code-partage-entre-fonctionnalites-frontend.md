# ADR 0006 – Code partagé entre fonctionnalités du frontend : `src/api`

- **Statut** : accepté
- **Date** : 2026-11-22 (lot S4)

## Contexte
La règle 05 interdit à une fonctionnalité d'importer une autre fonctionnalité (`eslint-plugin-boundaries`) et indique que « le code partagé descend dans `ui` ou `api` ». Elle décrit pourtant `src/api` comme « le client généré et son unique adaptateur ».

Le tableau de bord (lot S4) a besoin des mêmes appels que `chantiers` et `etapes` : la liste des chantiers, la transition d'une étape, et l'invalidation du cache après une transition. Recopier ces appels dans chaque fonctionnalité aurait dupliqué du code et multiplié les clés de cache.

Le squelette avait déjà ouvert la voie avec `api/clesRequetes.ts` et `api/profil.ts`.

## Décision
`src/api` peut contenir, en plus du client généré et de son adaptateur :
- des **fonctions d'appel partagées**, nommées par ressource (`api/chantiers.ts`, `api/transitions.ts`). Ce sont de simples appels au client, sans React ;
- les **clés de cache** de TanStack Query (`api/clesRequetes.ts`) ;
- des **fonctions d'invalidation** partagées (`api/rafraichissement.ts`). Elles reçoivent le `QueryClient` en paramètre et n'utilisent que son type.
- les **aides propres au client**, sans React non plus : la traduction d'une réponse d'erreur en erreur affichable (`api/erreurApi.ts`), la règle de nouvelle tentative des requêtes (`api/reessai.ts`) et le profil courant (`api/profil.ts`). Ce dernier lit et écrit `localStorage` et écoute `window` : ces accès au navigateur restent confinés à `src/api`, et le reste du frontend passe par ses fonctions.

- les **options de requête partagées** (clé et fonction d'appel réunies, par exemple `optionsListeChantiers`), et la lecture des en-têtes de réponse (`X-Liste-Tronquee`) ;
- la classe `ErreurApi`, qui expose le message global et le message de chaque champ d'un 422 (ADR 0008), et `donneesOuErreur`. `erreurApi.ts` déclare `ErreurApi` comme type d'erreur par défaut de TanStack Query (`declare module '@tanstack/react-query'`), ce qui ne lie `src/api` qu'aux types de la bibliothèque ;
- les appels de capacités (`api/capacites.ts`, `GET /api/moi`).

Les aides et données de test partagées vivent dans `src/test`, importable par les seuls fichiers `*.test.*` (règle `boundaries`).

Ce qui reste interdit dans `src/api` :
- les hooks React (`useQuery`, `useMutation`, `use…`) et les composants : ils restent dans les `services` de chaque fonctionnalité ;
- toute règle métier : comme partout dans le frontend, les droits et les calculs viennent de l'API ;
- toute importation de `features`, `ui` ou `app`.

## Conséquences
- Une fonctionnalité de vue d'ensemble (le tableau de bord) réutilise les appels des autres sans les importer : le découpage par fonctionnalité et les règles de `boundaries` restent inchangés.
- La ligne « `api` » de la règle 05 est ajustée pour refléter cette décision.
- Les fonctions de `src/api` sont testées à travers les hooks qui les utilisent. Un test direct est ajouté dès qu'une fonction porte une logique propre.
