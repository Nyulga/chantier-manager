// Blocs ESLint du sens des dépendances (règle 05) :
// - `eslint-plugin-boundaries` impose qui peut importer qui entre les sous-couches ;
// - `no-restricted-imports` réserve Radix à `src/ui` et openapi-fetch à `src/api` ;
// - `no-restricted-globals` réserve `fetch` à `src/api` ;
// - `import/no-cycle` interdit les imports circulaires.
import boundaries from 'eslint-plugin-boundaries';
import importPlugin from 'eslint-plugin-import';

const EXTENSIONS = ['.ts', '.tsx', '.js'];
const FICHIERS_SOURCE = ['src/**/*.{ts,tsx}'];

/** Types d'éléments de l'architecture : un par sous-couche (règle 05). */
const ELEMENTS = [
  { type: 'app', pattern: 'src/app', partialMatch: false },
  { type: 'api', pattern: 'src/api', partialMatch: false },
  { type: 'ui', pattern: 'src/ui', partialMatch: false },
  // Aides et données de test (serveur simulé, fabriques) : réservées aux fichiers de test.
  { type: 'aides-test', pattern: 'src/test', partialMatch: false },
  ...['pages', 'components', 'services'].map((sousCouche) => ({
    type: sousCouche,
    pattern: `src/features/*/${sousCouche}`,
    capture: ['fonctionnalite'],
    partialMatch: false,
  })),
];

/** Catégorie des fichiers de test : ils peuvent utiliser `src/test`, ce que le code de production ne peut pas. */
const CATEGORIE_TEST = 'test';
const FICHIERS_DE_TEST = [{ pattern: 'src/**/*.test.{ts,tsx}', category: CATEGORIE_TEST }];

/** Sélecteur d'un élément de la même fonctionnalité que le fichier qui importe. */
const memeFonctionnalite = (type) => ({
  element: { type, captured: { fonctionnalite: '{{ from.element.captured.fonctionnalite }}' } },
});

/**
 * Qui peut importer qui. Tout ce qui n'est pas listé est interdit (`default: 'disallow'`),
 * y compris `features/A` vers `features/B` : le code partagé descend dans `ui` ou `api`.
 */
const POLITIQUES_DEPENDANCES = [
  {
    from: { file: { categories: CATEGORIE_TEST } },
    allow: [
      { to: { element: { type: 'aides-test' } } },
      // Un test peut vérifier une correspondance de types (par exemple `StatutEtape` et le schéma
      // généré), mais n'appelle jamais `src/api` ni ne traverse les couches avec des valeurs.
      { to: { element: { type: ['api', 'ui'] } }, dependency: { kind: 'type' } },
    ],
  },
  {
    from: { element: { type: 'aides-test' } },
    allow: {
      to: { element: { type: ['api', 'ui', 'services', 'components', 'pages'] } },
    },
  },
  { from: { element: { type: 'app' } }, allow: { to: { element: { type: ['pages', 'ui'] } } } },
  {
    from: { element: { type: 'pages' } },
    allow: [
      { to: memeFonctionnalite('services') },
      { to: memeFonctionnalite('components') },
      { to: { element: { type: 'ui' } } },
    ],
  },
  {
    from: { element: { type: 'components' } },
    // Un composant reçoit tout par ses props : il ne peut importer que les *types* des services.
    allow: [
      { to: { element: { type: 'ui' } } },
      { to: memeFonctionnalite('services'), dependency: { kind: 'type' } },
    ],
  },
  { from: { element: { type: 'services' } }, allow: { to: { element: { type: 'api' } } } },
];

/** Règle `boundaries/dependencies`, avec un message qui renvoie vers la règle 05. */
function blocBoundaries({ racine }) {
  return {
    files: FICHIERS_SOURCE,
    plugins: { boundaries },
    settings: {
      'boundaries/elements': ELEMENTS,
      'boundaries/files': FICHIERS_DE_TEST,
      'boundaries/root-path': racine,
    },
    rules: {
      'boundaries/dependencies': [
        'error',
        {
          default: 'disallow',
          policies: POLITIQUES_DEPENDANCES,
          message:
            'Dépendance interdite : « {{ from.element.type }} » ne peut pas importer « {{ to.element.type }} » (règle 05).',
        },
      ],
    },
  };
}

/** `import/no-cycle` : les imports circulaires sont interdits, avec ou sans alias `@/`. */
function blocCycles({ racine }) {
  return {
    files: FICHIERS_SOURCE,
    plugins: { import: importPlugin },
    settings: {
      // Sans ces réglages, eslint-plugin-import ignore les fichiers TypeScript.
      'import/extensions': EXTENSIONS,
      'import/parsers': { '@typescript-eslint/parser': ['.ts', '.tsx'] },
      'import/resolver': {
        typescript: { project: `${racine}/tsconfig.app.json` },
      },
    },
    rules: { 'import/no-cycle': ['error', { maxDepth: Infinity }] },
  };
}

const MOTIF_RADIX = {
  group: ['@radix-ui/*', 'radix-ui'],
  message: 'Radix ne s’importe que dans src/ui : ajoute ou complète un composant du design system.',
};
const MOTIF_OPENAPI_FETCH = {
  group: ['openapi-fetch', 'openapi-typescript-helpers'],
  message: 'openapi-fetch ne s’importe que dans src/api : passe par un hook de services.',
};
const IMPORT_AXIOS = {
  name: 'axios',
  message: 'axios est interdit : le client est src/api/client.ts.',
};

/** Une configuration `no-restricted-imports` qui interdit axios et les motifs donnés. */
const restreindreImports = (motifs) => ({
  rules: { 'no-restricted-imports': ['error', { paths: [IMPORT_AXIOS], patterns: motifs }] },
});

/** Restrictions d'import propres à chaque dossier : les listes ne se cumulent pas entre blocs. */
function blocsImportsRestreints() {
  return [
    {
      files: FICHIERS_SOURCE,
      ignores: ['src/ui/**', 'src/api/**'],
      ...restreindreImports([MOTIF_RADIX, MOTIF_OPENAPI_FETCH]),
    },
    { files: ['src/ui/**/*.{ts,tsx}'], ...restreindreImports([MOTIF_OPENAPI_FETCH]) },
    { files: ['src/api/**/*.{ts,tsx}'], ...restreindreImports([MOTIF_RADIX]) },
  ];
}

/** `fetch` n'existe que dans `src/api` : ailleurs, on passe par les hooks de `services`. */
function blocFetchInterdit() {
  const message = 'fetch est réservé à src/api : appelle l’API depuis un hook de services.';

  return {
    files: FICHIERS_SOURCE,
    ignores: ['src/api/**'],
    rules: {
      'no-restricted-globals': ['error', { name: 'fetch', message }],
      'no-restricted-properties': [
        'error',
        { object: 'window', property: 'fetch', message },
        { object: 'globalThis', property: 'fetch', message },
      ],
    },
  };
}

/** @param {{ racine: string }} options */
export function blocDependances({ racine }) {
  return [
    blocBoundaries({ racine }),
    blocCycles({ racine }),
    ...blocsImportsRestreints(),
    blocFetchInterdit(),
  ];
}
