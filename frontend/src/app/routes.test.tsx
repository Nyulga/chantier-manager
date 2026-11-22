// Tests de la table des routes : chaque adresse mène à la bonne page, sous l'en-tête commun.
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { render, screen } from '@testing-library/react';
import { http, HttpResponse } from 'msw';
import { MemoryRouter } from 'react-router';
import { expect, it } from 'vitest';

import { installerServeurApi } from '@/ui/test/serveurApiSimule';

import { RoutesApplication } from './routes';

const serveur = installerServeurApi();

const ID = '0198f1a0-0000-7000-8000-000000000001';
const CHANTIER = {
  id: ID,
  nom: 'Rénovation de la mairie',
  adresse: { voie: '12 rue des Lilas', code_postal: '69003', ville: 'Lyon' },
  client: 'Mairie de Lyon',
  date_debut: '2026-03-02',
  echeance: '2026-09-30',
  budget: '18450.00',
  avancement: 0,
  peut_ajouter_etape: true,
  etapes_validees: 0,
  etapes_total: 0,
  etapes_a_valider: 0,
  jours_restants: 54,
  en_retard: false,
};

function afficher(adresse: string) {
  render(
    <QueryClientProvider
      client={new QueryClient({ defaultOptions: { queries: { retry: false } } })}
    >
      <MemoryRouter initialEntries={[adresse]}>
        <RoutesApplication />
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

it('affiche le tableau de bord à l’adresse racine, avec la barre latérale', async () => {
  serveur.use(
    http.get('/api/chantiers', () => HttpResponse.json([CHANTIER])),
    http.get('/api/etapes/a-valider', () => HttpResponse.json([])),
    http.get('/api/activite', () => HttpResponse.json([])),
  );

  afficher('/');

  expect(screen.getByRole('navigation', { name: 'Navigation principale' })).toBeVisible();
  expect(screen.getByRole('heading', { level: 1, name: 'Tableau de bord' })).toBeVisible();
  expect(await screen.findByRole('heading', { level: 3, name: CHANTIER.nom })).toBeVisible();
});

it('affiche la liste complète des chantiers à /chantiers', async () => {
  serveur.use(http.get('/api/chantiers', () => HttpResponse.json([CHANTIER])));

  afficher('/chantiers');

  expect(screen.getByRole('heading', { level: 1, name: 'Chantiers' })).toBeVisible();
  expect(await screen.findByRole('heading', { level: 2, name: CHANTIER.nom })).toBeVisible();
});

it('affiche le formulaire de création à /chantiers/nouveau', () => {
  afficher('/chantiers/nouveau');

  expect(screen.getByRole('heading', { level: 1, name: 'Nouveau chantier' })).toBeVisible();
});

it('affiche le détail du chantier avec ses étapes à /chantiers/:id', async () => {
  serveur.use(
    http.get(`/api/chantiers/${ID}`, () => HttpResponse.json(CHANTIER)),
    http.get(`/api/chantiers/${ID}/etapes`, () => HttpResponse.json([])),
  );

  afficher(`/chantiers/${ID}`);

  expect(await screen.findByRole('heading', { level: 1, name: CHANTIER.nom })).toBeVisible();
  expect(await screen.findByText('Aucune étape pour le moment.')).toBeVisible();
});

it('affiche la page 404 pour une adresse inconnue', () => {
  afficher('/n-importe-quoi');

  expect(screen.getByRole('heading', { level: 1, name: 'Page introuvable' })).toBeVisible();
});
