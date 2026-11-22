// Tests du hook `useTransitionEtape` : le corps envoyé, les invalidations et les erreurs de l'API.
import { act, renderHook, waitFor } from '@testing-library/react';
import { http, HttpResponse } from 'msw';
import { expect, it, vi } from 'vitest';

import { creerClientRequetes, creerEnveloppe } from '@/api/test/enveloppeRequetes';
import { installerServeurApi } from '@/api/test/serveurApiSimule';

import { etapeDeTest } from './etapeDeTest';
import { useTransitionEtape } from './useTransitionEtape';

const serveur = installerServeurApi();
const ETAPE = etapeDeTest({ statut: 'en_cours' });

it('envoie l’action et le commentaire à l’API', async () => {
  let corps: unknown = null;
  serveur.use(
    http.post(`/api/etapes/${ETAPE.id}/transitions`, async ({ request }) => {
      corps = await request.json();
      return HttpResponse.json(ETAPE);
    }),
  );
  const { result } = renderHook(() => useTransitionEtape(), {
    wrapper: creerEnveloppe(creerClientRequetes()),
  });

  act(() => {
    result.current.mutate({ etapeId: ETAPE.id, action: 'refuser', commentaire: 'Mal fini' });
  });

  await waitFor(() => {
    expect(result.current.data).toEqual(ETAPE);
  });
  expect(corps).toEqual({ action: 'refuser', commentaire: 'Mal fini' });
});

it('invalide la liste, le chantier concerné (avancement) et ses étapes', async () => {
  serveur.use(http.post(`/api/etapes/${ETAPE.id}/transitions`, () => HttpResponse.json(ETAPE)));
  const client = creerClientRequetes();
  const invalider = vi.spyOn(client, 'invalidateQueries');
  const { result } = renderHook(() => useTransitionEtape(), { wrapper: creerEnveloppe(client) });

  act(() => {
    result.current.mutate({ etapeId: ETAPE.id, action: 'valider' });
  });

  await waitFor(() => {
    expect(invalider).toHaveBeenCalledTimes(3);
  });
  expect(invalider).toHaveBeenCalledWith({ queryKey: ['chantiers', 'liste'] });
  expect(invalider).toHaveBeenCalledWith({ queryKey: ['chantiers', ETAPE.chantier_id] });
  expect(invalider).toHaveBeenCalledWith({
    queryKey: ['chantiers', ETAPE.chantier_id, 'etapes'],
  });
});

it('expose le message de l’API quand la transition est refusée (422)', async () => {
  serveur.use(
    http.post(`/api/etapes/${ETAPE.id}/transitions`, () =>
      HttpResponse.json(
        { status: 422, detail: 'Le commentaire du refus est obligatoire.' },
        { status: 422, headers: { 'Content-Type': 'application/problem+json' } },
      ),
    ),
  );
  const { result } = renderHook(() => useTransitionEtape(), {
    wrapper: creerEnveloppe(creerClientRequetes()),
  });

  act(() => {
    result.current.mutate({ etapeId: ETAPE.id, action: 'refuser' });
  });

  await waitFor(() => {
    expect(result.current.error?.message).toBe('Le commentaire du refus est obligatoire.');
  });
});
