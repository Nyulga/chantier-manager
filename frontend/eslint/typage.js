// Bloc ESLint du typage strict : `typescript-eslint` en mode « strict-type-checked », plus les
// interdits de la règle 05 (`any`, assertions `as`, `!`, commentaires `@ts-ignore`).
import globals from 'globals';
import tseslint from 'typescript-eslint';

/** @param {{ racine: string }} options */
export function blocTypage({ racine }) {
  return {
    files: ['**/*.{ts,tsx}'],
    extends: [tseslint.configs.strictTypeChecked],
    languageOptions: {
      globals: { ...globals.browser, ...globals.node },
      parserOptions: { projectService: true, tsconfigRootDir: racine },
    },
    rules: {
      '@typescript-eslint/no-explicit-any': 'error',
      // `as const` reste permis ; toute autre assertion de type est interdite.
      '@typescript-eslint/consistent-type-assertions': ['error', { assertionStyle: 'never' }],
      '@typescript-eslint/no-non-null-assertion': 'error',
      '@typescript-eslint/ban-ts-comment': [
        'error',
        {
          'ts-expect-error': true,
          'ts-ignore': true,
          'ts-nocheck': true,
          'ts-check': false,
        },
      ],
    },
  };
}
