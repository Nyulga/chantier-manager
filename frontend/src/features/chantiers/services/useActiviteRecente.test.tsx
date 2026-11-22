// Tests du hook `useActiviteRecente` : le fil vient de l'API, avec la limite demandée.
import { renderHook, waitFor } from '@testing-library/react';
import { http, HttpResponse } from 'msw';
import { expect, it } from 'vitest';

import { creerClientRequetes, creerEnveloppe } from '@/api/test/enveloppeRequetes';
import { installerServeurApi } from '@/api/test/serveurApiSimule';

import { activiteDeTest } from './activiteDeTest';
import { useActiviteRecente } from './useActiviteRecente';

const serveur = installerServeurApi();

it('renvoie les entrées de l’API, de la plus récente à la plus ancienne', async () => {
  const entrees = [activiteDeTest(), activiteDeTest({ nouveau_statut: 'validee', role: 'chef' })];
  serveur.use(http.get('/api/activite', () => HttpResponse.json(entrees)));

  const { result } = renderHook(() => useActiviteRecente(), {
    wrapper: creerEnveloppe(creerClientRequetes()),
  });

  await waitFor(() => {
    expect(result.current.data).toEqual(entrees);
  });
});

it('transmet la limite demandée à l’API', async () => {
  let limiteRecue: string | null = null;
  serveur.use(
    http.get('/api/activite', ({ request }) => {
      limiteRecue = new URL(request.url).searchParams.get('limite');
      return HttpResponse.json([]);
    }),
  );

  const { result } = renderHook(() => useActiviteRecente(7), {
    wrapper: creerEnveloppe(creerClientRequetes()),
  });

  await waitFor(() => {
    expect(result.current.isSuccess).toBe(true);
  });
  expect(limiteRecue).toBe('7');
});

it('expose le détail en français d’une erreur de l’API', async () => {
  serveur.use(
    http.get('/api/activite', () =>
      HttpResponse.json(
        { status: 422, detail: 'Limite invalide.' },
        { status: 422, headers: { 'Content-Type': 'application/problem+json' } },
      ),
    ),
  );

  const { result } = renderHook(() => useActiviteRecente(), {
    wrapper: creerEnveloppe(creerClientRequetes()),
  });

  await waitFor(() => {
    expect(result.current.error?.message).toBe('Limite invalide.');
  });
});
