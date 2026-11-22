// Tests de la page d'accueil : titre du produit, état de l'API (simulée avec MSW) et accessibilité.
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { render, screen } from '@testing-library/react';
import { http, HttpResponse } from 'msw';
import { setupServer } from 'msw/node';
import { afterAll, afterEach, beforeAll, expect, it } from 'vitest';

import { verifierAccessibilite } from '@/ui/test/verifierAccessibilite';

import { PageAccueil } from './PageAccueil';

const serveur = setupServer();

beforeAll(() => {
  serveur.listen({ onUnhandledFrame: 'error' });
});
afterEach(() => {
  serveur.resetHandlers();
});
afterAll(() => {
  serveur.close();
});

/** Affiche la page avec un cache de requêtes neuf, comme le fait `Providers` en production. */
function afficherPage() {
  return render(
    <QueryClientProvider client={new QueryClient()}>
      <PageAccueil />
    </QueryClientProvider>,
  );
}

it("affiche le nom de l'application en titre principal", () => {
  serveur.use(http.get('/api/health', () => HttpResponse.json({ statut: 'ok' })));

  afficherPage();

  expect(screen.getByRole('heading', { level: 1, name: 'Chantier Manager' })).toBeVisible();
});

it("annonce que l'état de l'API est en cours de vérification, puis qu'elle est disponible", async () => {
  serveur.use(http.get('/api/health', () => HttpResponse.json({ statut: 'ok' })));

  afficherPage();

  expect(screen.getByText('État de l’API : vérification en cours…')).toBeVisible();
  expect(await screen.findByText('État de l’API : disponible.')).toBeVisible();
});

it("annonce que l'API est indisponible quand elle ne répond pas", async () => {
  serveur.use(http.get('/api/health', () => new HttpResponse(null, { status: 503 })));

  afficherPage();

  expect(await screen.findByText('État de l’API : indisponible.')).toBeVisible();
});

it("n'a aucun défaut d'accessibilité détectable par axe", async () => {
  serveur.use(http.get('/api/health', () => HttpResponse.json({ statut: 'ok' })));

  const { container } = afficherPage();
  await screen.findByText('État de l’API : disponible.');

  await verifierAccessibilite(container);
});
