// Tests du hook `useActiviteRecente` : le fil vient de l'API, qui seule décide de sa taille.
import { waitFor } from '@testing-library/react';
import { http, HttpResponse } from 'msw';
import { expect, it } from 'vitest';

import { activiteDeTest } from '@/test/activiteDeTest';
import { reponseProbleme } from '@/test/reponseProbleme';
import { afficherHook } from '@/test/afficherHook';
import { installerServeurApi } from '@/test/serveurApiSimule';
import { testerReessai } from '@/test/testerReessai';

import { useActiviteRecente } from './useActiviteRecente';

const serveur = installerServeurApi();

function afficher() {
  return afficherHook(() => useActiviteRecente());
}

it("renvoie les entrées de l'API, de la plus récente à la plus ancienne", async () => {
  const entrees = [activiteDeTest(), activiteDeTest({ nouveau_statut: 'validee', role: 'chef' })];
  serveur.use(http.get('/api/activite', () => HttpResponse.json(entrees)));

  const { result } = afficher();

  await waitFor(() => {
    expect(result.current.data).toEqual(entrees);
  });
});

it("n'impose aucune limite : l'API décide de la taille du fil", async () => {
  let adresse = '';
  serveur.use(
    http.get('/api/activite', ({ request }) => {
      adresse = request.url;
      return HttpResponse.json([]);
    }),
  );

  const { result } = afficher();

  await waitFor(() => {
    expect(result.current.isSuccess).toBe(true);
  });
  expect(new URL(adresse).searchParams.has('limite')).toBe(false);
});

it("expose le détail en français d'une erreur de l'API", async () => {
  serveur.use(http.get('/api/activite', () => reponseProbleme(503, 'Service indisponible.')));

  const { result } = afficher();

  await waitFor(() => {
    expect(result.current.error?.message).toBe('Service indisponible.');
  });
});

testerReessai({
  serveur,
  chemin: '/api/activite',
  corps: [],
  utiliser: useActiviteRecente,
});
