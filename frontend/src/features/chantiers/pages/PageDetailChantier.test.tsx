// Tests de la page « détail du chantier » : informations, budget visible ou non, erreurs et page introuvable.
import { screen } from '@testing-library/react';
import { http, HttpResponse } from 'msw';
import { Route, Routes } from 'react-router';
import { expect, it } from 'vitest';

import { afficherAvecFournisseurs } from '@/test/afficherAvecFournisseurs';
import { chantierDeTest } from '@/test/chantierDeTest';
import { reponseProbleme } from '@/test/reponseProbleme';
import { installerServeurApi } from '@/test/serveurApiSimule';
import { verifierAccessibilite } from '@/test/verifierAccessibilite';

import { PageDetailChantier } from './PageDetailChantier';

const serveur = installerServeurApi();

/** Chantier tel que l'API le renvoie : le type vient de la fabrique de test. */
type Chantier = ReturnType<typeof chantierDeTest>;

function afficherAdresse(adresse: string) {
  return afficherAvecFournisseurs(
    <Routes>
      <Route path="/chantiers/:id" element={<PageDetailChantier />}>
        <Route index element={<p>Étapes du chantier</p>} />
      </Route>
    </Routes>,
    adresse,
  );
}

function afficherPage(chantier: Chantier) {
  serveur.use(http.get(`/api/chantiers/${chantier.id}`, () => HttpResponse.json(chantier)));
  return afficherAdresse(`/chantiers/${chantier.id}`);
}

it('affiche les informations du chantier, dont le budget formaté', async () => {
  afficherPage(chantierDeTest());

  expect(
    await screen.findByRole('heading', { level: 1, name: 'Rénovation de la mairie' }),
  ).toBeVisible();
  expect(screen.getByText('12 rue des Lilas, 69003 Lyon')).toBeVisible();
  expect(screen.getByText('Client : Mairie de Lyon')).toBeVisible();
  expect(screen.getByText('Du 02/03/2026 au 30/09/2026')).toBeVisible();
  expect(screen.getByText(/^Budget : 18\s450,00\s€$/)).toBeVisible();
});

it("n'affiche pas le budget quand l'API ne le donne pas", async () => {
  afficherPage(chantierDeTest({ budget: null }));

  await screen.findByRole('heading', { level: 1 });
  expect(screen.queryByText(/Budget/)).not.toBeInTheDocument();
});

it('affiche la page des étapes sous les informations, une fois le chantier chargé', async () => {
  afficherPage(chantierDeTest());

  expect(await screen.findByText('Étapes du chantier')).toBeVisible();
});

it('annonce le chargement, sans afficher les étapes ni les informations', () => {
  serveur.use(http.get('/api/chantiers/lent', () => new Promise(() => undefined)));

  afficherAdresse('/chantiers/lent');

  expect(screen.getByText('Chargement du chantier…')).toBeVisible();
  expect(screen.queryByText('Étapes du chantier')).not.toBeInTheDocument();
});

it("affiche la page introuvable quand l'API répond 404, par exemple pour un identifiant mal formé", async () => {
  serveur.use(http.get('/api/chantiers/abc', () => reponseProbleme(404, 'Chantier introuvable.')));

  afficherAdresse('/chantiers/abc');

  expect(await screen.findByRole('heading', { level: 1, name: 'Page introuvable' })).toBeVisible();
  expect(screen.queryByRole('alert')).not.toBeInTheDocument();
  expect(screen.queryByText('Étapes du chantier')).not.toBeInTheDocument();
});

it("affiche le message de l'API pour une autre erreur, et propose de revenir à la liste", async () => {
  serveur.use(
    http.get('/api/chantiers/panne', () => reponseProbleme(503, 'Service indisponible.')),
  );

  afficherAdresse('/chantiers/panne');

  expect(await screen.findByRole('alert')).toHaveTextContent('Service indisponible.');
  expect(screen.getByRole('link', { name: 'Retour aux chantiers' })).toHaveAttribute(
    'href',
    '/chantiers',
  );
});

it("n'a aucun défaut d'accessibilité détectable par axe", async () => {
  const { container } = afficherPage(chantierDeTest());
  await screen.findByRole('heading', { level: 1 });

  await verifierAccessibilite(container);
});

it('propose de revenir à la liste des chantiers', async () => {
  afficherPage(chantierDeTest());

  expect(await screen.findByRole('link', { name: 'Retour aux chantiers' })).toHaveAttribute(
    'href',
    '/chantiers',
  );
});
