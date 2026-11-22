// Tests du hook `useEtapesAValider` : la liste vient de l'API, qui seule décide du refus (403).
import { renderHook, waitFor } from '@testing-library/react';
import { http, HttpResponse } from 'msw';
import { afterEach, expect, it } from 'vitest';

import { creerClientRequetes, creerEnveloppe } from '@/api/test/enveloppeRequetes';
import { installerServeurApi } from '@/api/test/serveurApiSimule';

import { etapeAValiderDeTest } from './etapeAValiderDeTest';
import { estAccesRefuse, useEtapesAValider } from './useEtapesAValider';

const serveur = installerServeurApi();

afterEach(() => {
  localStorage.clear();
});

it('renvoie les étapes à valider de l’API, dans son ordre', async () => {
  const etapes = [etapeAValiderDeTest(), etapeAValiderDeTest({ id: 'autre', titre: 'Faïence' })];
  serveur.use(http.get('/api/etapes/a-valider', () => HttpResponse.json(etapes)));

  const { result } = renderHook(() => useEtapesAValider(), {
    wrapper: creerEnveloppe(creerClientRequetes()),
  });

  await waitFor(() => {
    expect(result.current.data).toEqual(etapes);
  });
});

it('envoie la requête même pour un ouvrier : c’est l’API qui décide, pas le profil', async () => {
  localStorage.setItem('chantier-manager.profil', 'ouvrier');
  const etapes = [etapeAValiderDeTest()];
  serveur.use(http.get('/api/etapes/a-valider', () => HttpResponse.json(etapes)));

  const { result } = renderHook(() => useEtapesAValider(), {
    wrapper: creerEnveloppe(creerClientRequetes()),
  });

  await waitFor(() => {
    expect(result.current.data).toEqual(etapes);
  });
});

it('reconnaît un refus 403 de l’API, sans rejouer la requête', async () => {
  let appels = 0;
  serveur.use(
    http.get('/api/etapes/a-valider', () => {
      appels += 1;
      return HttpResponse.json(
        { status: 403, detail: 'Action réservée à un chef.' },
        { status: 403, headers: { 'Content-Type': 'application/problem+json' } },
      );
    }),
  );

  const { result } = renderHook(() => useEtapesAValider(), {
    wrapper: creerEnveloppe(creerClientRequetes()),
  });

  await waitFor(() => {
    expect(estAccesRefuse(result.current.error)).toBe(true);
  });
  expect(appels).toBe(1);
});

it('ne prend pas une autre erreur pour un refus d’accès', async () => {
  serveur.use(
    http.get('/api/etapes/a-valider', () =>
      HttpResponse.json(
        { status: 500, detail: 'Le service est indisponible.' },
        { status: 500, headers: { 'Content-Type': 'application/problem+json' } },
      ),
    ),
  );

  const { result } = renderHook(() => useEtapesAValider(), {
    wrapper: creerEnveloppe(creerClientRequetes()),
  });

  await waitFor(() => {
    expect(result.current.error?.message).toBe('Le service est indisponible.');
  });
  expect(estAccesRefuse(result.current.error)).toBe(false);
});

it('rejoue la requête après une panne passagère, contrairement à un refus 403', async () => {
  const etapes = [etapeAValiderDeTest()];
  let appels = 0;
  serveur.use(
    http.get('/api/etapes/a-valider', () => {
      appels += 1;
      return appels === 1
        ? HttpResponse.json(
            { status: 500, detail: 'Le service est indisponible.' },
            { status: 500, headers: { 'Content-Type': 'application/problem+json' } },
          )
        : HttpResponse.json(etapes);
    }),
  );

  const { result } = renderHook(() => useEtapesAValider(), {
    wrapper: creerEnveloppe(creerClientRequetes()),
  });

  await waitFor(() => {
    expect(result.current.data).toEqual(etapes);
  });
  expect(appels).toBe(2);
});
