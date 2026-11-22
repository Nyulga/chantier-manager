// Tests du hook `useValiderEtape` : l'action envoyée, et la relecture de tout ce que la validation change.
import { act, renderHook, waitFor } from '@testing-library/react';
import { http, HttpResponse } from 'msw';
import { expect, it } from 'vitest';

import { creerClientRequetes, creerEnveloppe } from '@/api/test/enveloppeRequetes';
import { installerServeurApi } from '@/api/test/serveurApiSimule';

import { activiteDeTest } from './activiteDeTest';
import { chantierDeTest } from './chantierDeTest';
import { etapeAValiderDeTest } from './etapeAValiderDeTest';
import { useActiviteRecente } from './useActiviteRecente';
import { useChantiers } from './useChantiers';
import { useEtapesAValider } from './useEtapesAValider';
import { useValiderEtape } from './useValiderEtape';

const serveur = installerServeurApi();
const ETAPE = etapeAValiderDeTest();

it('envoie l’action « valider » pour l’étape', async () => {
  let corps: unknown = null;
  serveur.use(
    http.post(`/api/etapes/${ETAPE.id}/transitions`, async ({ request }) => {
      corps = await request.json();
      return HttpResponse.json({ ...ETAPE, statut: 'validee' });
    }),
  );
  const { result } = renderHook(() => useValiderEtape(), {
    wrapper: creerEnveloppe(creerClientRequetes()),
  });

  act(() => {
    result.current.mutate(ETAPE);
  });

  await waitFor(() => {
    expect(result.current.isSuccess).toBe(true);
  });
  expect(corps).toEqual({ action: 'valider' });
});

/** Sonde : les trois lectures du tableau de bord, dans le même cache que la mutation. */
function useSonde() {
  return {
    aValider: useEtapesAValider(),
    activite: useActiviteRecente(),
    chantiers: useChantiers(),
    validation: useValiderEtape(),
  };
}

/** Répond aux trois lectures en comptant les appels : l'étape disparaît dès la deuxième lecture. */
function simulerLectures() {
  const lectures = { aValider: 0, activite: 0, chantiers: 0 };
  serveur.use(
    http.get('/api/etapes/a-valider', () => {
      lectures.aValider += 1;
      return HttpResponse.json(lectures.aValider === 1 ? [ETAPE] : []);
    }),
    http.get('/api/activite', () => {
      lectures.activite += 1;
      return HttpResponse.json([activiteDeTest()]);
    }),
    http.get('/api/chantiers', () => {
      lectures.chantiers += 1;
      return HttpResponse.json([chantierDeTest()]);
    }),
  );
  return lectures;
}

it('relit les étapes à valider, l’activité et les chantiers après la validation', async () => {
  const lectures = simulerLectures();
  serveur.use(http.post(`/api/etapes/${ETAPE.id}/transitions`, () => HttpResponse.json(ETAPE)));
  const { result } = renderHook(() => useSonde(), {
    wrapper: creerEnveloppe(creerClientRequetes()),
  });
  await waitFor(() => {
    expect(result.current.aValider.data).toHaveLength(1);
  });
  await waitFor(() => {
    expect(result.current.chantiers.isSuccess).toBe(true);
  });

  act(() => {
    result.current.validation.mutate(ETAPE);
  });

  await waitFor(() => {
    expect(result.current.aValider.data).toEqual([]);
  });
  await waitFor(() => {
    expect(lectures.chantiers).toBe(2);
  });
  expect(lectures.activite).toBe(2);
});

it('relit aussi les données après un conflit (409), et expose le message de l’API', async () => {
  const lectures = simulerLectures();
  serveur.use(
    http.post(`/api/etapes/${ETAPE.id}/transitions`, () =>
      HttpResponse.json(
        { status: 409, detail: 'Cette étape a déjà changé de statut.' },
        { status: 409, headers: { 'Content-Type': 'application/problem+json' } },
      ),
    ),
  );
  const { result } = renderHook(() => useSonde(), {
    wrapper: creerEnveloppe(creerClientRequetes()),
  });
  await waitFor(() => {
    expect(result.current.aValider.data).toHaveLength(1);
  });
  await waitFor(() => {
    expect(result.current.chantiers.isSuccess).toBe(true);
  });

  act(() => {
    result.current.validation.mutate(ETAPE);
  });

  await waitFor(() => {
    expect(result.current.aValider.data).toEqual([]);
  });
  await waitFor(() => {
    expect(lectures.chantiers).toBe(2);
  });
  expect(result.current.validation.error?.message).toBe('Cette étape a déjà changé de statut.');
});
