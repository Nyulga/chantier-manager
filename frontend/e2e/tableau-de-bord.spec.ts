// Tableau de bord contre l'API réelle, à 360 px et à 1280 px : le chef valide depuis `/`.
import AxeBuilder from '@axe-core/playwright';
import { expect, test } from '@playwright/test';

import { signalerUneEtape } from './aides';

test('le chef valide une étape signalée depuis le tableau de bord', async ({ page }, info) => {
  // Un nom unique par projet et par essai : la base est partagée entre les tests parallèles et les reprises.
  const suffixe = `${info.project.name} ${Date.now().toString(36)}`;
  const nom = `Tableau de bord ${suffixe}`;
  const etape = `Fondations ${suffixe}`;

  await signalerUneEtape(page, nom, etape);
  await page.getByRole('link', { name: 'Tableau de bord' }).click();

  const aValider = page.getByRole('region', { name: 'À valider' });
  const ligne = aValider.getByRole('listitem').filter({ hasText: etape });
  await expect(ligne.getByText(nom)).toBeVisible();
  const examiner = ligne.getByRole('link', { name: `Examiner : ${etape}` });
  const adresseChantier = await examiner.getAttribute('href');

  await ligne.getByRole('button', { name: `Valider : ${etape}` }).click();

  await expect(aValider.getByText(etape)).toHaveCount(0);
  // Le bouton cliqué disparaît avec sa ligne : le focus ne doit pas retomber sur la page entière.
  await expect
    .poll(() => page.evaluate(() => document.activeElement === document.body))
    .toBe(false);
  // L'aperçu du tableau de bord ne montre que quelques chantiers : l'avancement se vérifie sur le chantier.
  await page.goto(adresseChantier ?? '/chantiers');
  await expect(page.getByRole('progressbar', { name: 'Avancement du chantier' })).toHaveAttribute(
    'aria-valuenow',
    '100',
  );
  await page.getByRole('link', { name: 'Tableau de bord' }).click();
  // On cible l'entrée par le titre unique de l'étape : le fil ne garde que les plus récentes.
  await expect(
    page.getByRole('list', { name: 'Activité récente' }).getByText(`Tu as validé « ${etape} »`),
  ).toBeVisible();
});

test('le tableau de bord n’a pas de défilement horizontal ni de défaut d’accessibilité', async ({
  page,
}, info) => {
  // Une étape à valider existe toujours : le bloc jaune, sa pastille et ses rayures sont rendus.
  const suffixe = `${info.project.name} ${Date.now().toString(36)}`;
  const etape = `Armatures ${suffixe}`;
  await signalerUneEtape(page, `Accessibilité ${suffixe}`, etape);
  await page.goto('/');
  await expect(page.getByRole('heading', { level: 1, name: 'Tableau de bord' })).toBeVisible();
  const ligne = page
    .getByRole('region', { name: 'À valider' })
    .getByRole('listitem')
    .filter({ hasText: etape });
  await expect(ligne).toBeVisible();
  await page.evaluate(() => document.fonts.ready);

  const debordement = await page.evaluate(
    () => document.documentElement.scrollWidth - document.documentElement.clientWidth,
  );
  // Axe tourne dans le vrai navigateur : il vérifie aussi les contrastes, que jsdom ne calcule pas.
  const clair = await new AxeBuilder({ page }).analyze();
  await expect(ligne).toHaveCSS('background-color', 'rgb(255, 248, 230)');
  await page.emulateMedia({ colorScheme: 'dark' });
  await expect(ligne).toHaveCSS('background-color', 'rgb(42, 36, 18)');
  const sombre = await new AxeBuilder({ page }).analyze();

  expect(debordement).toBeLessThanOrEqual(0);
  expect(clair.violations).toEqual([]);
  expect(sombre.violations).toEqual([]);
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
