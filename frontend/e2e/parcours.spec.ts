// Parcours complet contre l'API réelle : le chef crée un chantier et ses étapes, l'ouvrier les
// fait avancer, le chef refuse puis valide. Joué à 360 px et à 1280 px (voir playwright.config.ts).
import { expect, test, type Page } from '@playwright/test';

/** Choisit le profil dans l'en-tête : les droits et les boutons viennent ensuite de l'API. */
async function choisirProfil(page: Page, profil: 'Chef' | 'Ouvrier') {
  await page.getByRole('radio', { name: profil }).check();
}

async function creerChantier(page: Page, nom: string) {
  await page.goto('/');
  await page.getByRole('link', { name: 'Nouveau chantier' }).click();
  await page.getByLabel('Nom du chantier').fill(nom);
  await page.getByLabel('Voie').fill('12 rue des Lilas');
  await page.getByLabel('Code postal').fill('69003');
  await page.getByLabel('Ville').fill('Lyon');
  await page.getByLabel('Client').fill('Mairie de Lyon');
  await page.getByLabel('Date de début').fill('2026-03-02');
  await page.getByLabel('Échéance').fill('2026-09-30');
  await page.getByLabel('Budget (en euros)').fill('18450.00');
  await page.getByRole('button', { name: 'Créer le chantier' }).click();
  await expect(page.getByRole('heading', { level: 2, name: nom })).toBeVisible();
}

async function ajouterEtape(page: Page, titre: string) {
  await page.getByLabel('Titre de l’étape').fill(titre);
  await page.getByRole('button', { name: 'Ajouter l’étape' }).click();
  await expect(page.getByRole('heading', { level: 3, name: titre })).toBeVisible();
}

test('le chef et l’ouvrier font avancer un chantier jusqu’à 50 %', async ({ page }, info) => {
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

  await choisirProfil(page, 'Chef');
  await page.getByRole('button', { name: 'Refuser : Fondations' }).click();
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
});

test('la page 404 propose de revenir à la liste', async ({ page }) => {
  await page.goto('/une-page-qui-n-existe-pas');

  await expect(page.getByRole('heading', { level: 2, name: 'Page introuvable' })).toBeVisible();
  await page.getByRole('link', { name: 'Retour aux chantiers' }).click();
  await expect(page.getByRole('heading', { level: 2, name: 'Chantiers' })).toBeVisible();
});
