// Bloc ESLint de React : règles recommandées, JSX moderne et règles des hooks.
import react from 'eslint-plugin-react';
import reactHooks from 'eslint-plugin-react-hooks';

export function blocReact() {
  return {
    files: ['src/**/*.{ts,tsx}'],
    extends: [
      react.configs.flat.recommended,
      react.configs.flat['jsx-runtime'],
      reactHooks.configs.flat.recommended,
    ],
    settings: { react: { version: 'detect' } },
  };
}
