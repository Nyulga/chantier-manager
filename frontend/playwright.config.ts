// Configuration de Playwright : tests de bout en bout sur Chromium, contre le serveur de
// prévisualisation de Vite (le site construit), à 360 px (mobile) et à 1280 px (ordinateur).
import { defineConfig, devices } from '@playwright/test';

const PORT_PREVISUALISATION = 4173;

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
  webServer: {
    // On construit puis on prévisualise : le test porte sur ce qui sera réellement servi.
    command: `pnpm build && pnpm preview --host 127.0.0.1 --port ${String(PORT_PREVISUALISATION)} --strictPort`,
    url: `http://127.0.0.1:${String(PORT_PREVISUALISATION)}`,
    reuseExistingServer: !process.env['CI'],
    timeout: 120_000,
  },
});
