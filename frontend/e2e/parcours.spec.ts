// Parcours complet contre l'API réelle : le chef crée un chantier et ses étapes, l'ouvrier les
// fait avancer, le chef refuse puis valide. Joué à 360 px et à 1280 px (voir playwright.config.ts).
import { expect, test } from '@playwright/test';

import { ajouterEtape, choisirProfil, creerChantier } from './aides';

test("le chef et l'ouvrier font avancer un chantier jusqu'à 50 %", async ({ page }, info) => {
  // Un nom par projet : les deux tailles d'écran partagent la même base.
  const nom = `Chantier ${info.project.name}`;

  await creerChantier(page, nom);
  await expect(page.getByText(/Budget : 18\s450,00\s€/)).toBeVisible();
  await ajouterEtape(page, 'Fondations');
  await ajouterEtape(page, 'Gros œuvre');

  await choisirProfil(page, 'Ouvrier');
  await expect(page.getByText(/Budget/)).toHaveCount(0);
  await page.getByRole('button', { name: 'Démarrer : Fondations' }).click();
  await page.getByRole('button', { name: 'Signaler terminée : Fondations' }).click();
  await expect(page.getByText('Terminée (à valider)')).toBeVisible();
  await expect(page.getByRole('button', { name: /^Valider/ })).toHaveCount(0);
  await expect(page.getByRole('button', { name: /^Refuser/ })).toHaveCount(0);

  await choisirProfil(page, 'Chef');
  await page.getByRole('button', { name: 'Refuser : Fondations' }).click();
  // Sans commentaire, l'API refuse : son message apparaît sous le champ du motif.
  await page.getByRole('button', { name: 'Confirmer le refus' }).click();
  await expect(page.getByLabel('Motif du refus')).toHaveAccessibleDescription(/\S/);
  await page.getByLabel('Motif du refus').fill('Le coffrage est à reprendre.');
  await page.getByRole('button', { name: 'Confirmer le refus' }).click();
  await expect(page.getByText('En cours')).toBeVisible();

  await choisirProfil(page, 'Ouvrier');
  await page.getByRole('button', { name: 'Signaler terminée : Fondations' }).click();
  await choisirProfil(page, 'Chef');
  await page.getByRole('button', { name: 'Valider : Fondations' }).click();

  await expect(page.getByText('Validée')).toBeVisible();
  await expect(page.getByRole('progressbar', { name: 'Avancement du chantier' })).toHaveAttribute(
    'aria-valuenow',
    '50',
  );
  await expect(page.getByText('50 %')).toBeVisible();

  // La liste relit l'avancement : la carte du chantier affiche aussi 50 %.
  await page.getByRole('link', { name: 'Retour aux chantiers' }).click();
  await expect(page.getByRole('progressbar', { name: `Avancement de ${nom}` })).toHaveAttribute(
    'aria-valuenow',
    '50',
  );
});

test('la page 404 propose de revenir au tableau de bord', async ({ page }) => {
  await page.goto('/une-page-qui-n-existe-pas');

  await expect(page.getByRole('heading', { level: 1, name: 'Page introuvable' })).toBeVisible();
  await page.getByRole('link', { name: 'Retour au tableau de bord' }).click();
  await expect(page.getByRole('heading', { level: 1, name: 'Tableau de bord' })).toBeVisible();
});
