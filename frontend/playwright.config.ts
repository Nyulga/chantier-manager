// Configuration de Playwright : tests de bout en bout sur Chromium, contre le site construit
// (prévisualisation de Vite) et l'API réelle, à 360 px (mobile) et à 1280 px (ordinateur).
import { mkdtempSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';

import { defineConfig, devices } from '@playwright/test';

const PORT_PREVISUALISATION = 4173;
const PORT_API = 8000;

/*
 * Chaque exécution a sa propre base SQLite, dans un dossier temporaire : les tests ne dépendent
 * pas des données d'un lancement précédent et ne touchent jamais à la base de développement.
 * Les processus de test relisent ce fichier : le dossier est donc créé une seule fois, par le
 * processus principal, puis transmis aux autres par l'environnement.
 */
const dossierBase = process.env['E2E_DOSSIER_BASE'] ?? mkdtempSync(join(tmpdir(), 'chantier-e2e-'));
process.env['E2E_DOSSIER_BASE'] = dossierBase;
const urlBase = `sqlite:///${join(dossierBase, 'chantier.db').replaceAll('\\', '/')}`;

export default defineConfig({
  testDir: './e2e',
  fullyParallel: true,
  forbidOnly: Boolean(process.env['CI']),
  retries: process.env['CI'] ? 2 : 0,
  reporter: [['list'], ['html', { open: 'never' }]],
  use: {
    baseURL: `http://127.0.0.1:${String(PORT_PREVISUALISATION)}`,
    trace: 'on-first-retry',
  },
  projects: [
    {
      name: 'mobile-360',
      use: { ...devices['Desktop Chrome'], viewport: { width: 360, height: 740 } },
    },
    {
      name: 'ordinateur-1280',
      use: { ...devices['Desktop Chrome'], viewport: { width: 1280, height: 800 } },
    },
  ],
  webServer: [
    {
      // L'API réelle, démarrée depuis le backend ; ses migrations s'appliquent au démarrage.
      // `--no-dev` : sans lui, `uv run` réinstallerait le groupe `dev` et annulerait le
      // `uv sync --no-dev` de la CI ; l'API n'a besoin d'aucun outil de développement.
      command: `uv run --no-dev uvicorn app.main:creer_application --factory --host 127.0.0.1 --port ${String(PORT_API)}`,
      cwd: '../backend',
      // Les parcours e2e enchaînent bien plus d'écritures et de lectures que la limite de débit de la
      // démo (20 et 120 par minute et par adresse) : on la relève ici. Les seuils de production sont
      // testés côté backend.
      env: {
        CHANTIER_URL_BASE: urlBase,
        CHANTIER_ECRITURES_PAR_MINUTE: '100000',
        CHANTIER_LECTURES_PAR_MINUTE: '100000',
      },
      url: `http://127.0.0.1:${String(PORT_API)}/api/health`,
      reuseExistingServer: false,
      timeout: 120_000,
    },
    {
      // On construit puis on prévisualise : le test porte sur ce qui sera réellement servi.
      // `vite preview` transmet `/api` à l'API (même proxy que `vite dev`, voir vite.config.ts).
      command: `pnpm build && pnpm preview --host 127.0.0.1 --port ${String(PORT_PREVISUALISATION)} --strictPort`,
      url: `http://127.0.0.1:${String(PORT_PREVISUALISATION)}`,
      reuseExistingServer: !process.env['CI'],
      timeout: 120_000,
    },
  ],
});
