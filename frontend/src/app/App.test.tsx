// Test de l'application assemblée : les fournisseurs et les routes affichent l'accueil.
import { render, screen } from '@testing-library/react';
import { http, HttpResponse } from 'msw';
import { setupServer } from 'msw/node';
import { afterAll, beforeAll, expect, it } from 'vitest';

import { App } from './App';

// L'accueil interroge l'API : on la simule pour qu'aucune requête réelle ne parte pendant le test.
const serveur = setupServer(http.get('/api/health', () => HttpResponse.json({ statut: 'ok' })));

beforeAll(() => {
  serveur.listen({ onUnhandledFrame: 'error' });
});
afterAll(() => {
  serveur.close();
});

it("affiche la page d'accueil au démarrage", async () => {
  render(<App />);

  expect(screen.getByRole('heading', { level: 1, name: 'Chantier Manager' })).toBeVisible();
  expect(await screen.findByText('État de l’API : disponible.')).toBeVisible();
});
