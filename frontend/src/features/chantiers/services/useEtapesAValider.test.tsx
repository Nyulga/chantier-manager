// Tests du hook `useEtapesAValider` : la liste vient de l'API pour un chef, et n'est jamais demandée à un ouvrier.
import { renderHook, waitFor } from '@testing-library/react';
import { http, HttpResponse } from 'msw';
import { afterEach, expect, it } from 'vitest';

import { creerClientRequetes, creerEnveloppe } from '@/api/test/enveloppeRequetes';
import { installerServeurApi } from '@/api/test/serveurApiSimule';

import { etapeAValiderDeTest } from './etapeAValiderDeTest';
import { useEtapesAValider } from './useEtapesAValider';

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

it('ne demande rien à l’API quand le profil est ouvrier (l’API répondrait 403)', () => {
  localStorage.setItem('chantier-manager.profil', 'ouvrier');

  const { result } = renderHook(() => useEtapesAValider(), {
    wrapper: creerEnveloppe(creerClientRequetes()),
  });

  expect(result.current.fetchStatus).toBe('idle');
  expect(result.current.data).toBeUndefined();
});

it('expose le détail en français d’une erreur de l’API', async () => {
  serveur.use(
    http.get('/api/etapes/a-valider', () =>
      HttpResponse.json(
        { status: 403, detail: 'Action réservée à un chef.' },
        { status: 403, headers: { 'Content-Type': 'application/problem+json' } },
      ),
    ),
  );

  const { result } = renderHook(() => useEtapesAValider(), {
    wrapper: creerEnveloppe(creerClientRequetes()),
  });

  await waitFor(() => {
    expect(result.current.error?.message).toBe('Action réservée à un chef.');
  });
});
