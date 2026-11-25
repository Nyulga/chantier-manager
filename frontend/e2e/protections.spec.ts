// Le champ piège `site_web` dans un vrai navigateur : invisible et inatteignable pour une
// personne (clavier, lecteur d'écran, affichage), sans effet sur un envoi normal. Les tests
// unitaires vérifient les attributs ; ici on vérifie ce que le navigateur en fait réellement.
import { expect, test, type Page } from '@playwright/test';

import { ajouterEtape, creerChantier } from './aides';

const PIEGE = 'input[name="site_web"]';
const TOURS_MAX = 80;

/** Nom de l'élément actif, ou une description de repli : sert à reconnaître le champ piège. */
async function elementActif(page: Page): Promise<string> {
  return page.evaluate(() => {
    const actif = document.activeElement;
    if (actif === null) return 'aucun||';
    return `${actif.tagName}|${actif.getAttribute('name') ?? ''}|${actif.textContent.trim()}`;
  });
}

/**
 * Parcourt la page entière avec Tab, jusqu'à revenir sur le premier élément atteint : un tour
 * complet. Le test échoue dès que le focus se pose sur `site_web`, et renvoie ce qui a été visité.
 */
async function parcourirAuClavier(page: Page): Promise<string[]> {
  await page.evaluate(() => {
    // Départ au tout début du document, comme un utilisateur qui arrive sur la page.
    if (document.activeElement instanceof HTMLElement) document.activeElement.blur();
  });
  const visites: string[] = [];
  for (let pas = 0; pas < TOURS_MAX; pas += 1) {
    await page.keyboard.press('Tab');
    const actif = await elementActif(page);
    expect(
      actif.split('|')[1],
      `le focus s'est posé sur le champ piège au pas ${String(pas)}`,
    ).not.toBe('site_web');
    if (visites.length > 0 && actif === visites[0]) return visites;
    visites.push(actif);
  }
  throw new Error(`Aucun tour complet en ${String(TOURS_MAX)} pas : la page ne boucle pas.`);
}

/** Le champ existe dans la page (un robot le voit) mais ni le clavier, ni l'accessibilité, ni l'écran ne le montrent. */
async function verifierInvisible(page: Page) {
  const piege = page.locator(PIEGE);
  await expect(piege).toHaveCount(1);

  // Arbre d'accessibilité : ni par rôle, ni par nom, ni dans l'instantané.
  await expect(page.getByRole('textbox', { name: /site/i })).toHaveCount(0);
  await expect(page.getByLabel(/site/i)).toHaveCount(0);
  expect(await page.locator('body').ariaSnapshot()).not.toContain('site_web');

  // Aucune place visible : c'est l'enveloppe du champ qui est réduite à 1 px et rogne son contenu
  // (le champ lui-même garde sa taille, mais hors de la zone visible) ; la page ne défile pas
  // non plus horizontalement.
  const boite = await piege.locator('xpath=..').boundingBox();
  expect(boite?.width ?? 0).toBeLessThanOrEqual(1);
  expect(boite?.height ?? 0).toBeLessThanOrEqual(1);
  const debordement = await page.evaluate(
    () => document.documentElement.scrollWidth - document.documentElement.clientWidth,
  );
  expect(debordement).toBeLessThanOrEqual(0);
}

async function ouvrirFormulaireChantier(page: Page) {
  await page.goto('/chantiers');
  await page.getByRole('link', { name: 'Nouveau chantier' }).click();
  await expect(page.getByLabel('Nom du chantier')).toBeVisible();
}

test('formulaire de chantier : le champ piège est hors clavier, hors accessibilité et hors écran', async ({
  page,
}) => {
  await ouvrirFormulaireChantier(page);

  const visites = await parcourirAuClavier(page);
  // Le tour a bien traversé le formulaire : il atteint le dernier bouton.
  expect(visites.some((visite) => visite.includes('Créer le chantier'))).toBe(true);
  await verifierInvisible(page);
});

test("ajout d'étape : le champ piège est hors clavier, hors accessibilité et hors écran", async ({
  page,
}, info) => {
  await creerChantier(page, `Piège étape ${info.project.name} ${Date.now().toString(36)}`);
  await expect(page.getByLabel("Titre de l'étape")).toBeVisible();

  const visites = await parcourirAuClavier(page);
  expect(visites.some((visite) => visite.includes("Ajouter l'étape"))).toBe(true);
  await verifierInvisible(page);
});

test('un humain crée un chantier : la requête ne contient pas `site_web`', async ({
  page,
}, info) => {
  const envoi = page.waitForRequest(
    (requete) => requete.method() === 'POST' && /\/api\/chantiers\/?$/.test(requete.url()),
  );
  const nom = `Humain chantier ${info.project.name} ${Date.now().toString(36)}`;

  await creerChantier(page, nom); // attend l'arrivée sur le détail : le chantier existe.

  const corps = (await envoi).postData() ?? '';
  expect(corps).toContain(nom);
  expect(corps).not.toContain('site_web');
});

test('un humain ajoute une étape : la requête ne contient pas `site_web`', async ({
  page,
}, info) => {
  await creerChantier(page, `Humain étape ${info.project.name} ${Date.now().toString(36)}`);
  const envoi = page.waitForRequest(
    (requete) =>
      requete.method() === 'POST' && /\/api\/chantiers\/[^/]+\/etapes\/?$/.test(requete.url()),
  );

  await ajouterEtape(page, 'Terrassement'); // attend l'étape dans la liste : elle existe.

  const corps = (await envoi).postData() ?? '';
  expect(corps).toContain('Terrassement');
  expect(corps).not.toContain('site_web');
});
