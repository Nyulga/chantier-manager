// Assemble la configuration ESLint complète du frontend à partir de blocs thématiques :
// base stricte, dépendances entre couches, design system et limites contre le code spaghetti.
// C'est une fonction (et non un simple objet) pour que les tests des garde-fous puissent
// l'appliquer à un projet de fixtures, avec exactement les mêmes règles que le vrai code.
import js from '@eslint/js';
import { defineConfig } from 'eslint/config';
import tseslint from 'typescript-eslint';

import { blocDependances } from './dependances.js';
import { blocDesignSystem } from './design-system.js';
import { blocLimites } from './limites.js';
import { blocReact } from './react.js';
import { blocTypage } from './typage.js';

/**
 * Construit la configuration ESLint du projet situé dans `racine`.
 *
 * @param {{ racine: string }} options `racine` : dossier qui contient `src/` et les `tsconfig`.
 */
export function creerConfig({ racine }) {
  return defineConfig(
    {
      ignores: [
        'dist/**',
        'coverage/**',
        'playwright-report/**',
        'test-results/**',
        // Violations volontaires qui servent de preuve aux garde-fous : jamais linté normalement.
        'tests/garde-fous/fixtures/**',
      ],
    },
    {
      // Interdit les commentaires `eslint-disable` : désactiver une règle est interdit (règle 00).
      linterOptions: { noInlineConfig: true, reportUnusedDisableDirectives: 'error' },
    },
    js.configs.recommended,
    // Les fichiers de configuration en JavaScript ne passent pas par le typage strict.
    {
      files: ['**/*.js'],
      extends: [tseslint.configs.disableTypeChecked],
    },
    blocTypage({ racine }),
    blocReact(),
    ...blocDependances({ racine }),
    ...blocDesignSystem(),
    blocLimites(),
  );
}
