---
paths:
  - "frontend/**"
---

# Règle 05 – Frontend (présentation visuelle)

Relire d'abord `00-principes.md`, puis `docs/design-system.md` (« Balise »).

## Rôle
Afficher les données de l'API et transmettre les actions de l'utilisateur. **Le frontend ne contient aucune règle métier** : la future application mobile utilisera la même API, et une règle dupliquée ici finirait par diverger.

## Les sous-couches du frontend
```
src/
├── app/                      # assemblage : routes, providers (session, thème, TanStack Query)
├── api/                      # client généré depuis OpenAPI + son unique adaptateur
├── ui/                       # design system Balise : SEUL endroit qui produit du HTML stylé
└── features/<fonctionnalite>/
    ├── services/             # hooks TanStack Query : SEULS à appeler src/api
    ├── components/           # composants propres à la fonctionnalité, faits de composants ui
    └── pages/                # écrans : utilisent services + components + ui
```

| Sous-couche | Peut importer | Ne peut **pas** |
|---|---|---|
| `pages` | `services` et `components` de la même fonctionnalité, `ui` | appeler `api`, utiliser du HTML brut ou des classes CSS |
| `components` | `ui`, les types de `services` | appeler `api` ou `services` (ils reçoivent tout par leurs props), utiliser du HTML brut ou des classes CSS |
| `services` | `api` | importer `ui`, `components` ou `pages` |
| `ui` | Radix, Tailwind (tokens du thème uniquement) | importer `features` ou `api` |
| `api` | openapi-fetch, les types générés | importer quoi que ce soit d'autre du projet |
| `features/A` | — | importer `features/B` (le code partagé descend dans `ui` ou `api`) |

Ces règles sont **vérifiées par ESLint** (`eslint-plugin-boundaries`, `no-restricted-imports`, `react/forbid-elements`, `react/forbid-dom-props`, `import/no-cycle`), configuré au lot 01.

## Composants du design system uniquement
- Hors de `src/ui`, sont interdits :
  - les éléments HTML interactifs ou stylés : `button`, `input`, `select`, `textarea`, `a`, `img`, `table` ;
  - les props `className` et `style`.

  Les pages et composants utilisent `Bouton`, `Champ`, `Badge`, `Carte`, `Pile`, `Grille`, `Page`, etc.
- Si un composant manque, on l'**ajoute dans `src/ui`**, conforme à Balise, avec son test. On ne bricole jamais localement.
- Dans `src/ui`, seuls les tokens du thème Tailwind sont utilisés. Sont interdits : les valeurs arbitraires (`bg-[#F2A900]`, `p-[13px]`) et les couleurs ou tailles en dur.
- Le jaune `accent` et les rayures sont réservés à ce que prévoit Balise (étapes à valider, bouton principal mobile, navigation active).

## Aucune règle métier
- On n'affiche un bouton (« Valider », « Refuser »…) que si **l'API l'indique** dans les actions permises de la réponse. Le frontend ne déduit jamais un droit du rôle.
- L'avancement, les statuts, les montants et la visibilité du budget viennent de l'API. Le frontend les **formate** (`src/ui/format/` : dates `JJ/MM/AAAA`, montants `18 450,00 €`), il ne les **calcule** pas.
- Les schémas zod des formulaires ne valident que la saisie (format, champ requis), pour le confort de l'utilisateur. **L'autorité reste l'API**, et ses erreurs 422 sont affichées sous les champs concernés.

## Patterns obligatoires
| Pattern | Application |
|---|---|
| **Feature modules** | L'organisation ci-dessus, en miroir des modules du backend. |
| **Custom hooks (couche service)** | `useChantier(id)`, `useSignalerEtapeTerminee()`… Toute la logique de données, de cache et d'invalidation est dans `services`. |
| **Presentational / Container** | Les `pages` récupèrent les données ; les `components` affichent ce qu'ils reçoivent par props et remontent les actions par callbacks. |
| **Provider** | Session, thème et client TanStack Query, déclarés dans `src/app`. Aucun store global de type Redux : l'état serveur vit dans TanStack Query, l'état local dans les composants. |
| **Adapter** | `src/api/client.ts` enveloppe le client généré (base `/api`, cookies, en-tête CSRF, rafraîchissement de session). `fetch` et `axios` sont interdits ailleurs. |

## Typage
- Les types de l'API sont **générés** depuis OpenAPI, jamais écrits à la main.
- `any`, `as` (sauf `as const`), `!` (non-null assertion) et `@ts-ignore` sont interdits.

## Accessibilité et langue
- WCAG 2.1 AA : chaque champ a un libellé visible, le focus est toujours visible, la couleur n'est jamais le seul indice, et les zones de toucher font au moins 44 px (52 à 56 px pour les actions principales sur mobile).
- Mobile d'abord. Vérifier l'affichage à 360, 768 et 1280 px.
- Tous les textes sont en français et tutoient l'utilisateur (`docs/design-system.md` §6).

## Tests (voir aussi `07-tests-et-migrations.md`)
- Vitest et Testing Library, avec une couverture **≥ 90 %**. On interroge l'interface par rôle et par libellé (`getByRole`), jamais par classe CSS.
- Chaque composant `ui` a un test d'accessibilité (axe).
- Les `services` sont testés en simulant l'API au niveau réseau (MSW), à partir des types générés.
