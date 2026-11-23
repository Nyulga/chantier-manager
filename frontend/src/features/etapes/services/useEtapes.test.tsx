// Tests du hook `useEtapes` : les étapes d'un chantier viennent de l'API, erreurs comprises.
import { waitFor } from '@testing-library/react';
import { http, HttpResponse } from 'msw';
import { expect, it } from 'vitest';

import { afficherHook } from '@/test/afficherHook';
import { installerServeurApi } from '@/test/serveurApiSimule';

import { etapeDeTest } from '@/test/etapeDeTest';
import { useEtapes } from './useEtapes';

const serveur = installerServeurApi();

it('renvoie les étapes du chantier', async () => {
  const etape = etapeDeTest();
  serveur.use(
    http.get(`/api/chantiers/${etape.chantier_id}/etapes`, () => HttpResponse.json([etape])),
  );

  const { result } = afficherHook(() => useEtapes(etape.chantier_id));

  await waitFor(() => {
    expect(result.current.data).toEqual([etape]);
  });
});

it("expose le message de l'API en cas d'erreur", async () => {
  serveur.use(
    http.get('/api/chantiers/inconnu/etapes', () =>
      HttpResponse.json(
        { status: 404, detail: 'Chantier introuvable.' },
        { status: 404, headers: { 'Content-Type': 'application/problem+json' } },
      ),
    ),
  );

  const { result } = afficherHook(() => useEtapes('inconnu'));

  await waitFor(() => {
    expect(result.current.error?.message).toBe('Chantier introuvable.');
  });
});
