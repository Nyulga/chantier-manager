// Tests du hook `useChantiers` : la liste vient de l'API (simulée avec MSW), erreurs comprises.
import { renderHook, waitFor } from '@testing-library/react';
import { http, HttpResponse } from 'msw';
import { afterEach, expect, it } from 'vitest';

import { creerClientRequetes, creerEnveloppe } from '@/api/test/enveloppeRequetes';
import { installerServeurApi } from '@/api/test/serveurApiSimule';

import { chantierDeTest } from './chantierDeTest';
import { useChantiers } from './useChantiers';

const serveur = installerServeurApi();

afterEach(() => {
  localStorage.clear();
});

it('renvoie les chantiers de l’API', async () => {
  const chantier = chantierDeTest();
  serveur.use(http.get('/api/chantiers', () => HttpResponse.json([chantier])));

  const { result } = renderHook(() => useChantiers(), {
    wrapper: creerEnveloppe(creerClientRequetes()),
  });

  await waitFor(() => {
    expect(result.current.data).toEqual([chantier]);
  });
});

it('envoie le profil choisi dans l’en-tête X-Profil', async () => {
  localStorage.setItem('chantier-manager.profil', 'ouvrier');
  let profilRecu: string | null = null;
  serveur.use(
    http.get('/api/chantiers', ({ request }) => {
      profilRecu = request.headers.get('X-Profil');
      return HttpResponse.json([]);
    }),
  );

  const { result } = renderHook(() => useChantiers(), {
    wrapper: creerEnveloppe(creerClientRequetes()),
  });

  await waitFor(() => {
    expect(result.current.isSuccess).toBe(true);
  });
  expect(profilRecu).toBe('ouvrier');
});

it('expose le détail en français d’une erreur de l’API', async () => {
  serveur.use(
    http.get('/api/chantiers', () =>
      HttpResponse.json(
        { status: 400, detail: 'Profil inconnu.' },
        { status: 400, headers: { 'Content-Type': 'application/problem+json' } },
      ),
    ),
  );

  const { result } = renderHook(() => useChantiers(), {
    wrapper: creerEnveloppe(creerClientRequetes()),
  });

  await waitFor(() => {
    expect(result.current.error?.message).toBe('Profil inconnu.');
  });
});
