// Tests de la page « liste des chantiers » : cartes, liste vide, lien de création et accessibilité.
import { screen } from '@testing-library/react';
import { http, HttpResponse } from 'msw';
import { Route, Routes } from 'react-router';
import { afterEach, expect, it } from 'vitest';

import { afficherAvecFournisseurs } from '@/ui/test/afficherAvecFournisseurs';
import { installerServeurApi } from '@/ui/test/serveurApiSimule';
import { verifierAccessibilite } from '@/ui/test/verifierAccessibilite';

import { chantierDeTest } from '../services/chantierDeTest';
import { PageListeChantiers } from './PageListeChantiers';

const serveur = installerServeurApi();

afterEach(() => {
  localStorage.clear();
});

function afficherPage() {
  return afficherAvecFournisseurs(
    <Routes>
      <Route path="/" element={<PageListeChantiers />} />
    </Routes>,
  );
}

it('affiche une carte par chantier : nom, ville, échéance, avancement et lien', async () => {
  const chantier = chantierDeTest();
  serveur.use(http.get('/api/chantiers', () => HttpResponse.json([chantier])));

  afficherPage();

  expect(await screen.findByRole('heading', { level: 3, name: chantier.nom })).toBeVisible();
  expect(screen.getByText('Lyon')).toBeVisible();
  expect(screen.getByText('Échéance : 30/09/2026')).toBeVisible();
  expect(
    screen.getByRole('progressbar', { name: `Avancement de ${chantier.nom}` }),
  ).toHaveAttribute('aria-valuenow', '50');
  expect(screen.getByRole('link', { name: `Ouvrir le chantier ${chantier.nom}` })).toHaveAttribute(
    'href',
    `/chantiers/${chantier.id}`,
  );
});

it('affiche un message quand il n’y a aucun chantier', async () => {
  serveur.use(http.get('/api/chantiers', () => HttpResponse.json([])));

  afficherPage();

  expect(await screen.findByText('Aucun chantier pour le moment.')).toBeVisible();
});

it('propose « Nouveau chantier » au profil chef', async () => {
  serveur.use(http.get('/api/chantiers', () => HttpResponse.json([])));

  afficherPage();

  expect(await screen.findByRole('link', { name: 'Nouveau chantier' })).toHaveAttribute(
    'href',
    '/chantiers/nouveau',
  );
});

it('ne propose pas « Nouveau chantier » au profil ouvrier', async () => {
  localStorage.setItem('chantier-manager.profil', 'ouvrier');
  serveur.use(http.get('/api/chantiers', () => HttpResponse.json([])));

  afficherPage();

  await screen.findByText('Aucun chantier pour le moment.');
  expect(screen.queryByRole('link', { name: 'Nouveau chantier' })).not.toBeInTheDocument();
});

it('affiche le message de l’API quand la liste ne peut pas être chargée', async () => {
  serveur.use(
    http.get('/api/chantiers', () =>
      HttpResponse.json(
        { status: 400, detail: 'Profil inconnu.' },
        { status: 400, headers: { 'Content-Type': 'application/problem+json' } },
      ),
    ),
  );

  afficherPage();

  expect(await screen.findByRole('alert')).toHaveTextContent('Profil inconnu.');
});

it('n’a aucun défaut d’accessibilité détectable par axe', async () => {
  serveur.use(http.get('/api/chantiers', () => HttpResponse.json([chantierDeTest()])));

  const { container } = afficherPage();
  await screen.findByRole('heading', { level: 3 });

  await verifierAccessibilite(container);
});
