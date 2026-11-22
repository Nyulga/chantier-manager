// Gestes réutilisés par les tests de bout en bout : choisir le profil, créer un chantier, ajouter une étape.
import { expect, type Page } from '@playwright/test';

/** Choisit le profil dans la barre latérale : les droits et les boutons viennent ensuite de l'API. */
export async function choisirProfil(page: Page, profil: 'Chef' | 'Ouvrier') {
  await page.getByRole('radio', { name: profil }).check();
}

/** Crée un chantier depuis la liste des chantiers et attend l'arrivée sur son détail. */
export async function creerChantier(page: Page, nom: string) {
  await page.goto('/chantiers');
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
  await expect(page.getByRole('heading', { level: 1, name: nom })).toBeVisible();
}

/** Ajoute une étape au chantier ouvert et attend qu'elle apparaisse dans la liste. */
export async function ajouterEtape(page: Page, titre: string) {
  await page.getByLabel('Titre de l’étape').fill(titre);
  await page.getByRole('button', { name: 'Ajouter l’étape' }).click();
  await expect(page.getByRole('heading', { level: 3, name: titre })).toBeVisible();
}

/**
 * Crée un chantier avec une étape que l'ouvrier signale terminée, puis repasse en chef : le chef
 * a ainsi au moins une étape « à valider ». Les noms doivent être uniques (la base est partagée).
 */
export async function signalerUneEtape(page: Page, nomChantier: string, titreEtape: string) {
  await creerChantier(page, nomChantier);
  await ajouterEtape(page, titreEtape);
  await choisirProfil(page, 'Ouvrier');
  await page.getByRole('button', { name: `Démarrer : ${titreEtape}` }).click();
  await page.getByRole('button', { name: `Signaler terminée : ${titreEtape}` }).click();
  await expect(page.getByText('Terminée (à valider)')).toBeVisible();
  await choisirProfil(page, 'Chef');
}
