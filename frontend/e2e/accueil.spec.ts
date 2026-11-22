// Test de bout en bout de la page d'accueil, à 360 px et à 1280 px (voir playwright.config.ts).
import { expect, test } from '@playwright/test';

test("la page d'accueil affiche le tableau de bord, le logo et le choix du profil", async ({
  page,
}) => {
  await page.goto('/');

  await expect(page.getByRole('heading', { level: 1, name: 'Tableau de bord' })).toBeVisible();
  await expect(page.getByText('Chantier Manager')).toBeVisible();
  await expect(page.getByRole('radiogroup', { name: 'Profil' })).toBeVisible();
});

test("la page d'accueil n'a pas de défilement horizontal", async ({ page }) => {
  await page.goto('/');

  const debordement = await page.evaluate(
    () => document.documentElement.scrollWidth - document.documentElement.clientWidth,
  );

  expect(debordement).toBeLessThanOrEqual(0);
});

test('les polices sont servies par le site lui-même, sans appel à un tiers', async ({ page }) => {
  const hotes = new Set<string>();
  page.on('request', (requete) => hotes.add(new URL(requete.url()).host));

  await page.goto('/');
  await page.evaluate(() => document.fonts.ready);

  expect([...hotes]).toEqual(['127.0.0.1:4173']);
});

test('le titre est écrit en Archivo condensé, en majuscules', async ({ page }) => {
  await page.goto('/');

  const titre = page.getByRole('heading', { level: 1, name: 'Tableau de bord' });

  await expect(titre).toHaveCSS('text-transform', 'uppercase');
  await expect(titre).toHaveCSS('font-stretch', '72%');
  await expect(titre).toHaveCSS('font-weight', '800');
  // La police variable est bien chargée depuis les fichiers du site (au moins une face trouvée).
  const faces = await page.evaluate(
    async () => (await document.fonts.load('800 28px "Archivo Variable"')).length,
  );
  expect(faces).toBeGreaterThan(0);
});

test('le thème sombre suit la préférence du système', async ({ page }) => {
  await page.emulateMedia({ colorScheme: 'dark' });
  await page.goto('/');

  await expect(page.locator('body')).toHaveCSS('background-color', 'rgb(23, 25, 28)');
});

test('le thème clair est le thème par défaut', async ({ page }) => {
  await page.emulateMedia({ colorScheme: 'light' });
  await page.goto('/');

  await expect(page.locator('body')).toHaveCSS('background-color', 'rgb(241, 240, 236)');
});
