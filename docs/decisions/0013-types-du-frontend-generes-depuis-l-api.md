# ADR 0013 – Les types du frontend sont générés depuis l'API

- **Statut** : accepté
- **Date** : 2026-11-24 (hors lot). Le choix est fait depuis le lot S1 (`CLAUDE.md` et règle 05). Cet ADR le consigne après coup.

## Contexte
Le frontend et la future application mobile appellent la même API. Si les types du frontend étaient écrits à la main, ils s'écarteraient peu à peu de l'API. Par exemple, un champ renommé côté backend casserait l'écran sans qu'aucun contrôle ne le voie. Le backend (FastAPI) produit déjà une description exacte de l'API : le schéma OpenAPI.

## Décision
- **Source unique** : le schéma OpenAPI de l'API est la seule source des types.
- **Génération** : `just client` l'exporte (`tools.exporter_openapi`), puis **openapi-typescript** en tire `frontend/src/api/schema.d.ts`. Ce fichier est versionné et n'est jamais modifié à la main.
- **Client** : **openapi-fetch** est un client HTTP léger, typé par ce fichier. Une route, un paramètre ou un champ qui n'existe pas fait échouer `tsc`.
- **Un seul client** (`src/api/client.ts`) : il connaît le préfixe `/api` et ajoute l'en-tête du profil. Ses erreurs sont converties en `ErreurApi` (ADR 0006 et 0008).
- **Règle de travail** : après tout changement de route ou de schéma côté backend, on relance `just client`, et le fichier régénéré part dans le même commit.

## Alternatives écartées
- **Types écrits à la main** : ils s'écartent de l'API sans que personne ne le voie, et chaque changement est fait deux fois.
- **axios ou `fetch` sans typage** : les erreurs de nom de champ ou de route n'apparaîtraient qu'à l'exécution.
- **Générateur de client complet (openapi-generator, orval)** : il produit beaucoup de code et impose sa façon d'appeler l'API, alors que TanStack Query gère déjà les appels (ADR 0009). openapi-fetch ajoute seulement le typage, sur `fetch`.
- **tRPC ou GraphQL** : ils imposeraient une autre façon d'écrire l'API. L'API REST documentée par OpenAPI doit rester utilisable telle quelle par l'application mobile.

## Conséquences
- **En bien** : un changement d'API qui casse le frontend est détecté par `tsc`, avant tout test. La documentation et les types ne peuvent pas diverger.
- **En mal** : il faut penser à relancer `just client`. Aujourd'hui, la CI ne vérifie pas que `schema.d.ts` est à jour : un oubli n'est repéré que si `tsc` ou un test échoue.
