// Tests du hook `useNombreChantiers` : le compteur de la navigation vient de la liste de l'API.
import { renderHook, waitFor } from '@testing-library/react';
import { http, HttpResponse } from 'msw';
import { expect, it } from 'vitest';

import { creerClientRequetes, creerEnveloppe } from '@/api/test/enveloppeRequetes';
import { installerServeurApi } from '@/api/test/serveurApiSimule';

import { useNombreChantiers } from './useNombreChantiers';

const serveur = installerServeurApi();

it('compte les chantiers que l’API renvoie', async () => {
  serveur.use(
    http.get('/api/chantiers', () =>
      HttpResponse.json([{ id: 'un' }, { id: 'deux' }, { id: 'trois' }]),
    ),
  );

  const { result } = renderHook(() => useNombreChantiers(), {
    wrapper: creerEnveloppe(creerClientRequetes()),
  });

  await waitFor(() => {
    expect(result.current).toBe(3);
  });
});

it('ne renvoie rien quand l’API échoue : la navigation n’affiche alors aucun compteur', async () => {
  let appels = 0;
  serveur.use(
    http.get('/api/chantiers', () => {
      appels += 1;
      return HttpResponse.json({}, { status: 500 });
    }),
  );

  const { result } = renderHook(() => useNombreChantiers(), {
    wrapper: creerEnveloppe(creerClientRequetes()),
  });

  await waitFor(() => {
    expect(appels).toBe(1);
  });
  expect(result.current).toBeUndefined();
});
