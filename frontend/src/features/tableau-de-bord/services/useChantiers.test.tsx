// Tests du hook `useChantiers` du tableau de bord : la liste vient de l'API, qui décide du périmètre.
import { waitFor } from '@testing-library/react';
import { http, HttpResponse } from 'msw';
import { expect, it } from 'vitest';

import { chantierDeTest } from '@/test/chantierDeTest';
import { afficherHook } from '@/test/afficherHook';
import { installerServeurApi } from '@/test/serveurApiSimule';

import { useChantiers } from './useChantiers';

const serveur = installerServeurApi();

it("renvoie les chantiers de l'API", async () => {
  const chantier = chantierDeTest();
  serveur.use(http.get('/api/chantiers', () => HttpResponse.json([chantier])));

  const { result } = afficherHook(() => useChantiers());

  await waitFor(() => {
    expect(result.current.data).toEqual([chantier]);
  });
});
