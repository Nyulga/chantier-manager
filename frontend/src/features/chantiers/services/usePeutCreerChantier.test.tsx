// Tests du hook `usePeutCreerChantier` : le droit de créer un chantier vient de l'API, jamais du profil.
import { waitFor } from '@testing-library/react';
import { afterEach, expect, it } from 'vitest';

import { gestionnaireCapacites } from '@/test/capacites';
import { afficherHook } from '@/test/afficherHook';
import { installerServeurApi } from '@/test/serveurApiSimule';

import { usePeutCreerChantier } from './usePeutCreerChantier';

const serveur = installerServeurApi();

afterEach(() => {
  localStorage.clear();
});

it.each([
  ['chef', true],
  ['ouvrier', false],
])("renvoie le droit annoncé par l'API pour le profil %s", async (profil, droit) => {
  localStorage.setItem('chantier-manager.profil', profil);
  serveur.use(gestionnaireCapacites);

  const { result } = afficherHook(() => usePeutCreerChantier());

  await waitFor(() => {
    expect(result.current.data).toBe(droit);
  });
});
