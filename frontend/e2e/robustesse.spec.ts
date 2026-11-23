// Robustesse des écrans contre l'API réelle, à 360 px et à 1280 px : débordement, 0 %, erreur par champ, ouvrier.
import { expect, test, type Page } from '@playwright/test';

import { ajouterEtape, creerChantier } from './aides';

/** Largeur en trop de la page : positive quand un défilement horizontal apparaît. */
async function debordement(page: Page) {
  await page.evaluate(() => document.fonts.ready);
  return page.evaluate(
    () => document.documentElement.scrollWidth - document.documentElement.clientWidth,
  );
}

test("le détail d'un chantier et ses étapes n'ont pas de défilement horizontal", async ({
  page,
}, info) => {
  const suffixe = `${info.project.name} ${Date.now().toString(36)}`;
  await creerChantier(page, `Débordement ${suffixe}`);
  await ajouterEtape(page, `Pose des fondations et du gros œuvre avec un titre long ${suffixe}`);
  await ajouterEtape(page, 'Charpente');

  expect(await debordement(page)).toBeLessThanOrEqual(0);
});

test('un chantier sans étape affiche 0 % sur son détail et sur sa carte', async ({
  page,
}, info) => {
  const nom = `Sans étape ${info.project.name} ${Date.now().toString(36)}`;

  await creerChantier(page, nom);

  await expect(page.getByRole('progressbar', { name: 'Avancement du chantier' })).toHaveAttribute(
    'aria-valuenow',
    '0',
  );
  await expect(page.getByText('0 %')).toBeVisible();
  await page.getByRole('link', { name: 'Retour aux chantiers' }).click();
  await expect(page.getByRole('progressbar', { name: `Avancement de ${nom}` })).toHaveAttribute(
    'aria-valuenow',
    '0',
  );
});

test('un code postal trop long est signalé sous son champ, sans quitter le formulaire', async ({
  page,
}) => {
  await page.goto('/chantiers/nouveau');
  await page.getByLabel('Nom du chantier').fill('Code postal trop long');
  await page.getByLabel('Voie').fill('12 rue des Lilas');
  await page.getByLabel('Code postal').fill('12345678901');
  await page.getByLabel('Ville').fill('Lyon');
  await page.getByLabel('Client').fill('Mairie de Lyon');
  await page.getByLabel('Date de début').fill('2026-03-02');
  await page.getByLabel('Échéance').fill('2026-09-30');
  await page.getByLabel('Budget (en euros)').fill('18450.00');

  await page.getByRole('button', { name: 'Créer le chantier' }).click();

  // Le message de l'API est lié au champ (annoncé par un lecteur d'écran), et seul ce champ est en erreur.
  await expect(page.getByLabel('Code postal')).toHaveAccessibleDescription(/10 caractères/);
  await expect(page.getByLabel('Code postal')).toHaveAttribute('aria-invalid', 'true');
  await expect(page.getByLabel('Ville')).not.toHaveAttribute('aria-invalid', 'true');
  await expect(page.getByRole('heading', { level: 1, name: 'Nouveau chantier' })).toBeVisible();
});

test("un ouvrier voit le tableau de bord sans section « À valider », et n'interroge pas l'API à ce sujet", async ({
  page,
}) => {
  const requetes: string[] = [];
  page.on('request', (requete) => requetes.push(new URL(requete.url()).pathname));
  await page.addInitScript(() => {
    localStorage.setItem('chantier-manager.profil', 'ouvrier');
  });

  await page.goto('/');

  await expect(page.getByRole('heading', { level: 1, name: 'Tableau de bord' })).toBeVisible();
  // Les droits (`/api/moi`) et les listes sont arrivés quand plus aucun « Chargement… » n'est affiché :
  // sans cette attente, `toHaveCount(0)` réussirait aussi avant que la section ait pu apparaître.
  await expect(page.getByText(/^Chargement/)).toHaveCount(0);
  await expect(page.getByRole('region', { name: 'À valider' })).toHaveCount(0);
  await expect(page.getByRole('link', { name: 'Nouveau chantier' })).toHaveCount(0);
  await expect(page.getByRole('heading', { level: 2, name: 'Mes chantiers' })).toBeVisible();
  expect(requetes).not.toContain('/api/etapes/a-valider');
});

test("un ouvrier qui ouvre la création d'un chantier lit une information, pas un formulaire", async ({
  page,
}) => {
  await page.addInitScript(() => {
    localStorage.setItem('chantier-manager.profil', 'ouvrier');
  });

  await page.goto('/chantiers/nouveau');

  await expect(page.getByText('Ton profil ne permet pas de créer un chantier.')).toBeVisible();
  await expect(page.getByLabel('Nom du chantier')).toHaveCount(0);
  await expect(page.getByRole('link', { name: 'Retour aux chantiers' })).toBeVisible();
});

test('un identifiant de chantier mal formé affiche la page introuvable', async ({ page }) => {
  await page.goto('/chantiers/abc');

  await expect(page.getByRole('heading', { level: 1, name: 'Page introuvable' })).toBeVisible();
});
