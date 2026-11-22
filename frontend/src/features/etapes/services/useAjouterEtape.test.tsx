// Tests du hook `useAjouterEtape` : le corps envoyé, les invalidations et les erreurs.
import { act, renderHook, waitFor } from '@testing-library/react';
import { http, HttpResponse } from 'msw';
import { expect, it, vi } from 'vitest';

import { creerClientRequetes, creerEnveloppe } from '@/api/test/enveloppeRequetes';
import { installerServeurApi } from '@/api/test/serveurApiSimule';

import { etapeDeTest } from './etapeDeTest';
import { useAjouterEtape } from './useAjouterEtape';

const serveur = installerServeurApi();
const CHANTIER = '0198f1a0-0000-7000-8000-000000000001';

it('envoie le titre à l’API et renvoie l’étape créée', async () => {
  let corps: unknown = null;
  serveur.use(
    http.post(`/api/chantiers/${CHANTIER}/etapes`, async ({ request }) => {
      corps = await request.json();
      return HttpResponse.json(etapeDeTest(), { status: 201 });
    }),
  );
  const { result } = renderHook(() => useAjouterEtape(CHANTIER), {
    wrapper: creerEnveloppe(creerClientRequetes()),
  });

  act(() => {
    result.current.mutate('Fondations');
  });

  await waitFor(() => {
    expect(result.current.data).toEqual(etapeDeTest());
  });
  expect(corps).toEqual({ titre: 'Fondations' });
});

it('invalide la liste et le chantier (avancement), dont les étapes dépendent par leur clé', async () => {
  serveur.use(
    http.post(`/api/chantiers/${CHANTIER}/etapes`, () =>
      HttpResponse.json(etapeDeTest(), { status: 201 }),
    ),
  );
  const client = creerClientRequetes();
  const invalider = vi.spyOn(client, 'invalidateQueries');
  const { result } = renderHook(() => useAjouterEtape(CHANTIER), {
    wrapper: creerEnveloppe(client),
  });

  act(() => {
    result.current.mutate('Fondations');
  });

  await waitFor(() => {
    expect(invalider).toHaveBeenCalledTimes(2);
  });
  expect(invalider).toHaveBeenCalledWith({ queryKey: ['chantiers', 'liste'] });
  expect(invalider).toHaveBeenCalledWith({ queryKey: ['chantiers', 'detail', CHANTIER] });
});

it('expose le message de l’API quand l’ajout est refusé', async () => {
  serveur.use(
    http.post(`/api/chantiers/${CHANTIER}/etapes`, () =>
      HttpResponse.json(
        { status: 403, detail: 'Seul un chef peut ajouter une étape.' },
        { status: 403, headers: { 'Content-Type': 'application/problem+json' } },
      ),
    ),
  );
  const { result } = renderHook(() => useAjouterEtape(CHANTIER), {
    wrapper: creerEnveloppe(creerClientRequetes()),
  });

  act(() => {
    result.current.mutate('Fondations');
  });

  await waitFor(() => {
    expect(result.current.error?.message).toBe('Seul un chef peut ajouter une étape.');
  });
});
