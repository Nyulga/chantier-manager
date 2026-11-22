// Tests de la table des routes : l'adresse `/` mène à la page d'accueil.
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { render, screen } from '@testing-library/react';
import { http, HttpResponse } from 'msw';
import { setupServer } from 'msw/node';
import { MemoryRouter } from 'react-router';
import { afterAll, beforeAll, expect, it } from 'vitest';

import { RoutesApplication } from './routes';

// L'accueil interroge l'API : on la simule pour qu'aucune requête réelle ne parte pendant le test.
const serveur = setupServer(http.get('/api/health', () => HttpResponse.json({ statut: 'ok' })));

beforeAll(() => {
  serveur.listen({ onUnhandledFrame: 'error' });
});
afterAll(() => {
  serveur.close();
});

it("affiche la page d'accueil à l'adresse racine", async () => {
  render(
    <QueryClientProvider client={new QueryClient()}>
      <MemoryRouter initialEntries={['/']}>
        <RoutesApplication />
      </MemoryRouter>
    </QueryClientProvider>,
  );

  expect(screen.getByRole('heading', { level: 1, name: 'Chantier Manager' })).toBeVisible();
  // On attend la réponse de l'API pour que la mise à jour de la page ait lieu pendant le test.
  expect(await screen.findByText('État de l’API : disponible.')).toBeVisible();
});
