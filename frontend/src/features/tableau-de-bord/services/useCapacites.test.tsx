// Tests du hook `useCapacites` : les droits viennent de l'API, et suivent le profil choisi.
import { act, waitFor } from '@testing-library/react';
import { delay, http, HttpResponse } from 'msw';
import { afterEach, expect, it } from 'vitest';

import { enregistrerProfil } from '@/api/profil';
import { CAPACITES_CHEF, CAPACITES_OUVRIER, gestionnaireCapacites } from '@/test/capacites';
import { reponseProbleme } from '@/test/reponseProbleme';
import { afficherHook } from '@/test/afficherHook';
import { installerServeurApi } from '@/test/serveurApiSimule';
import { testerReessai } from '@/test/testerReessai';

import { useCapacites } from './useCapacites';

const serveur = installerServeurApi();

afterEach(() => {
  localStorage.clear();
});

function afficher() {
  return afficherHook(() => useCapacites());
}

it("renvoie les capacités que l'API annonce pour le profil choisi", async () => {
  serveur.use(gestionnaireCapacites);

  const { result } = afficher();

  await waitFor(() => {
    expect(result.current.data).toEqual(CAPACITES_CHEF);
  });
});

it("n'affiche jamais les capacités de l'ancien profil pendant que celles du nouveau arrivent", async () => {
  serveur.use(
    http.get('/api/moi', async ({ request }) => {
      if (request.headers.get('X-Profil') === 'ouvrier') {
        await delay('infinite');
      }
      return HttpResponse.json(CAPACITES_CHEF);
    }),
  );
  const { result } = afficher();
  await waitFor(() => {
    expect(result.current.data).toEqual(CAPACITES_CHEF);
  });

  act(() => {
    enregistrerProfil('ouvrier');
  });

  await waitFor(() => {
    expect(result.current.isPending).toBe(true);
  });
  expect(result.current.data).toBeUndefined();
});

it("relit les capacités de l'ouvrier après un changement de profil", async () => {
  serveur.use(gestionnaireCapacites);
  const { result } = afficher();
  await waitFor(() => {
    expect(result.current.data).toEqual(CAPACITES_CHEF);
  });

  act(() => {
    enregistrerProfil('ouvrier');
  });

  await waitFor(() => {
    expect(result.current.data).toEqual(CAPACITES_OUVRIER);
  });
});

it("expose le message de l'API quand elle refuse", async () => {
  serveur.use(http.get('/api/moi', () => reponseProbleme(400, 'Profil inconnu.')));

  const { result } = afficher();

  await waitFor(() => {
    expect(result.current.error?.message).toBe('Profil inconnu.');
  });
});

testerReessai({
  serveur,
  chemin: '/api/moi',
  corps: CAPACITES_CHEF,
  utiliser: useCapacites,
});
