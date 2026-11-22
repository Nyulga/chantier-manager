// Tests du hook `useEtatApi` : l'API est simulée au niveau réseau avec MSW (règle 05).
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { renderHook, waitFor } from '@testing-library/react';
import { http, HttpResponse } from 'msw';
import { setupServer } from 'msw/node';
import type { ReactNode } from 'react';
import { afterAll, afterEach, beforeAll, expect, it } from 'vitest';

import { useEtatApi } from './useEtatApi';

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

/** Fournit un cache neuf à chaque test, pour qu'aucun résultat ne fuite d'un test à l'autre. */
function enveloppe({ children }: { readonly children: ReactNode }) {
  return <QueryClientProvider client={new QueryClient()}>{children}</QueryClientProvider>;
}

it("renvoie le statut de l'API quand elle répond", async () => {
  serveur.use(http.get('/api/health', () => HttpResponse.json({ statut: 'ok' })));

  const { result } = renderHook(() => useEtatApi(), { wrapper: enveloppe });

  await waitFor(() => {
    expect(result.current.data).toEqual({ statut: 'ok' });
  });
});

it("signale une erreur quand l'API répond par une erreur serveur", async () => {
  serveur.use(http.get('/api/health', () => new HttpResponse(null, { status: 500 })));

  const { result } = renderHook(() => useEtatApi(), { wrapper: enveloppe });

  await waitFor(() => {
    expect(result.current.isError).toBe(true);
  });
});

it("signale une erreur quand l'API est injoignable", async () => {
  serveur.use(http.get('/api/health', () => HttpResponse.error()));

  const { result } = renderHook(() => useEtatApi(), { wrapper: enveloppe });

  await waitFor(() => {
    expect(result.current.isError).toBe(true);
  });
});
