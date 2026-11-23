// Tests du hook `useChantiers` : la liste vient de l'API (simulée avec MSW), erreurs comprises.
import { waitFor } from '@testing-library/react';
import { http, HttpResponse } from 'msw';
import { afterEach, expect, it } from 'vitest';

import { afficherHook } from '@/test/afficherHook';
import { installerServeurApi } from '@/test/serveurApiSimule';

import { chantierDeTest } from '@/test/chantierDeTest';
import { testerReessai } from '@/test/testerReessai';

import { useChantiers } from './useChantiers';

const serveur = installerServeurApi();

afterEach(() => {
  localStorage.clear();
});

it("renvoie les chantiers de l'API, sous la forme que la carte affiche", async () => {
  const chantier = chantierDeTest();
  serveur.use(http.get('/api/chantiers', () => HttpResponse.json([chantier])));

  const { result } = afficherHook(() => useChantiers());

  await waitFor(() => {
    expect(result.current.data).toMatchObject([
      { id: chantier.id, nom: chantier.nom, adresse: '12 rue des Lilas, 69003 Lyon' },
    ]);
  });
});

it("envoie le profil choisi dans l'en-tête X-Profil", async () => {
  localStorage.setItem('chantier-manager.profil', 'ouvrier');
  let profilRecu: string | null = null;
  serveur.use(
    http.get('/api/chantiers', ({ request }) => {
      profilRecu = request.headers.get('X-Profil');
      return HttpResponse.json([]);
    }),
  );

  const { result } = afficherHook(() => useChantiers());

  await waitFor(() => {
    expect(result.current.isSuccess).toBe(true);
  });
  expect(profilRecu).toBe('ouvrier');
});

it("expose le détail en français d'une erreur de l'API", async () => {
  serveur.use(
    http.get('/api/chantiers', () =>
      HttpResponse.json(
        { status: 400, detail: 'Profil inconnu.' },
        { status: 400, headers: { 'Content-Type': 'application/problem+json' } },
      ),
    ),
  );

  const { result } = afficherHook(() => useChantiers());

  await waitFor(() => {
    expect(result.current.error?.message).toBe('Profil inconnu.');
  });
});

testerReessai({
  serveur,
  chemin: '/api/chantiers',
  corps: [],
  utiliser: useChantiers,
});
