// Configuration de Vite et de Vitest : plugins React et Tailwind, alias `@` vers `src`,
// proxy de développement pour l'API, et seuils de couverture des tests unitaires.
import { fileURLToPath } from 'node:url';

import tailwindcss from '@tailwindcss/vite';
import react from '@vitejs/plugin-react';
import { defineConfig } from 'vitest/config';

/** Seuil minimal de couverture du frontend, en pourcentage (intent.md, section 3.1). */
const SEUIL_COUVERTURE = 90;

export default defineConfig({
  plugins: [react(), tailwindcss()],
  resolve: {
    alias: { '@': fileURLToPath(new URL('./src', import.meta.url)) },
  },
  server: {
    // Le frontend et l'API partagent le même domaine : en développement, le proxy joue ce rôle.
    proxy: { '/api': 'http://127.0.0.1:8000' },
  },
  test: {
    environment: 'jsdom',
    setupFiles: ['./vitest.setup.ts'],
    include: ['src/**/*.test.{ts,tsx}', 'tests/**/*.test.ts'],
    coverage: {
      provider: 'v8',
      include: ['src/**/*.{ts,tsx}'],
      // `src/test` contient les aides des tests (serveur simulé, fabriques) : du code de test, pas de production.
      exclude: ['src/**/*.test.{ts,tsx}', 'src/**/*.d.ts', 'src/test/**'],
      reporter: ['text', 'html'],
      thresholds: {
        lines: SEUIL_COUVERTURE,
        branches: SEUIL_COUVERTURE,
        functions: SEUIL_COUVERTURE,
        statements: SEUIL_COUVERTURE,
      },
    },
  },
});
