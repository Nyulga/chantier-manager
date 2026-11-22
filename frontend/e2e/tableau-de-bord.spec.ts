// Tableau de bord contre l'API réelle, à 360 px et à 1280 px : le chef valide depuis `/`.
import AxeBuilder from '@axe-core/playwright';
import { expect, test } from '@playwright/test';

import { ajouterEtape, choisirProfil, creerChantier } from './aides';

test('le chef valide une étape signalée depuis le tableau de bord', async ({ page }, info) => {
  // Un nom par projet : les deux tailles d'écran partagent la même base.
  const nom = `Tableau de bord ${info.project.name}`;
  const etape = `Fondations ${info.project.name}`;

  await creerChantier(page, nom);
  await ajouterEtape(page, etape);
  await choisirProfil(page, 'Ouvrier');
  await page.getByRole('button', { name: `Démarrer : ${etape}` }).click();
  await page.getByRole('button', { name: `Signaler terminée : ${etape}` }).click();
  await expect(page.getByText('Terminée (à valider)')).toBeVisible();

  await choisirProfil(page, 'Chef');
  await page.getByRole('link', { name: 'Tableau de bord' }).click();

  const aValider = page.getByRole('region', { name: 'À valider' });
  await expect(aValider.getByText(etape)).toBeVisible();
  await expect(aValider.getByText(nom)).toBeVisible();
  await expect(aValider.getByRole('link', { name: `Examiner : ${etape}` })).toBeVisible();

  await aValider.getByRole('button', { name: `Valider : ${etape}` }).click();

  await expect(aValider.getByText(etape)).toHaveCount(0);
  const carte = page.getByRole('progressbar', { name: `Avancement de ${nom}` });
  await expect(carte).toHaveAttribute('aria-valuenow', '100');
  const activite = page.getByRole('list', { name: 'Activité récente' });
  await expect(activite.getByText(`as validé « ${etape} »`)).toBeVisible();
});

test('le tableau de bord n’a pas de défilement horizontal ni de défaut d’accessibilité', async ({
  page,
}) => {
  await page.goto('/');
  await expect(page.getByRole('heading', { level: 1, name: 'Tableau de bord' })).toBeVisible();
  await page.evaluate(() => document.fonts.ready);

  const debordement = await page.evaluate(
    () => document.documentElement.scrollWidth - document.documentElement.clientWidth,
  );
  // Axe tourne dans le vrai navigateur : il vérifie aussi les contrastes, que jsdom ne calcule pas.
  const resultats = await new AxeBuilder({ page }).analyze();

  expect(debordement).toBeLessThanOrEqual(0);
  expect(resultats.violations).toEqual([]);
});

test('la barre latérale propose la navigation et les entrées « Bientôt » désactivées', async ({
  page,
}) => {
  await page.goto('/');

  const navigation = page.getByRole('navigation', { name: 'Navigation principale' });
  await expect(navigation.getByRole('link', { name: 'Tableau de bord' })).toHaveAttribute(
    'aria-current',
    'page',
  );
  await expect(navigation.getByRole('link', { name: /Mes chantiers/ })).toHaveAttribute(
    'href',
    '/chantiers',
  );
  await expect(navigation.getByRole('link', { name: /Équipe/ })).toHaveCount(0);
  await expect(navigation.getByText('Bientôt')).toHaveCount(2);
  await expect(page.getByRole('searchbox', { name: 'Rechercher un chantier' })).toBeDisabled();
});

test('le focus clavier reste visible sur la barre latérale graphite', async ({ page }) => {
  await page.emulateMedia({ colorScheme: 'light' });
  await page.goto('/');
  const lien = page.getByRole('link', { name: /Mes chantiers/ });

  // Le contour global est de la couleur du texte (graphite) : sur la barre graphite il
  // deviendrait invisible, la barre le redéfinit donc en couleur de fond de page.
  await lien.focus();
  await page.keyboard.press('Shift+Tab');
  await page.keyboard.press('Tab');

  await expect(lien).toBeFocused();
  await expect(lien).toHaveCSS('outline-color', 'rgb(241, 240, 236)');
  await expect(lien).toHaveCSS('outline-width', '3px');
});
