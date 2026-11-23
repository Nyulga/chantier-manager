// Tests du hook `useCreerChantier` : le corps envoyé, la relecture de la liste et les erreurs.
import { act, waitFor } from '@testing-library/react';
import { http, HttpResponse } from 'msw';
import { expect, it } from 'vitest';

import { reponseProbleme } from '@/test/reponseProbleme';
import { afficherHook } from '@/test/afficherHook';
import { installerServeurApi } from '@/test/serveurApiSimule';

import { chantierDeTest } from '@/test/chantierDeTest';
import { useChantiers } from './useChantiers';
import { useCreerChantier, type SaisieChantier } from './useCreerChantier';

const serveur = installerServeurApi();

const SAISIE: SaisieChantier = {
  nom: 'Rénovation de la mairie',
  voie: '12 rue des Lilas',
  codePostal: '69003',
  ville: 'Lyon',
  client: 'Mairie de Lyon',
  dateDebut: '2026-03-02',
  echeance: '2026-09-30',
  budget: '18450.00',
};

it("envoie le chantier à l'API sous la forme attendue et renvoie le chantier créé", async () => {
  const cree = chantierDeTest();
  let corps: unknown = null;
  serveur.use(
    http.post('/api/chantiers', async ({ request }) => {
      corps = await request.json();
      return HttpResponse.json(cree, { status: 201 });
    }),
  );
  const { result } = afficherHook(() => useCreerChantier());

  act(() => {
    result.current.mutate(SAISIE);
  });

  await waitFor(() => {
    expect(result.current.data).toEqual(cree);
  });
  expect(corps).toEqual({
    nom: 'Rénovation de la mairie',
    adresse: { voie: '12 rue des Lilas', code_postal: '69003', ville: 'Lyon' },
    client: 'Mairie de Lyon',
    date_debut: '2026-03-02',
    echeance: '2026-09-30',
    budget: '18450.00',
  });
});

it('relit la liste des chantiers après la création : le nouveau chantier y figure', async () => {
  const cree = chantierDeTest();
  let liste: unknown[] = [];
  serveur.use(
    http.get('/api/chantiers', () => HttpResponse.json(liste)),
    http.post('/api/chantiers', () => {
      liste = [cree];
      return HttpResponse.json(cree, { status: 201 });
    }),
  );
  const { result } = afficherHook(() => ({
    chantiers: useChantiers(),
    creation: useCreerChantier(),
  }));
  await waitFor(() => {
    expect(result.current.chantiers.data).toEqual([]);
  });

  act(() => {
    result.current.creation.mutate(SAISIE);
  });

  await waitFor(() => {
    expect(result.current.chantiers.data).toEqual([cree]);
  });
});

it("expose le message de l'API quand la création est refusée", async () => {
  serveur.use(
    http.post('/api/chantiers', () => reponseProbleme(403, 'Seul un chef peut créer un chantier.')),
  );
  const { result } = afficherHook(() => useCreerChantier());

  act(() => {
    result.current.mutate(SAISIE);
  });

  await waitFor(() => {
    expect(result.current.error?.message).toBe('Seul un chef peut créer un chantier.');
  });
});

it("expose les erreurs par champ de l'API, avec le champ pointé de l'adresse", async () => {
  serveur.use(
    http.post('/api/chantiers', () =>
      reponseProbleme(422, 'Les données envoyées sont invalides.', [
        { champ: 'adresse.code_postal', message: 'Le code postal est trop long.' },
      ]),
    ),
  );
  const { result } = afficherHook(() => useCreerChantier());

  act(() => {
    result.current.mutate(SAISIE);
  });

  await waitFor(() => {
    expect(result.current.error?.erreurs).toEqual([
      { champ: 'adresse.code_postal', message: 'Le code postal est trop long.' },
    ]);
  });
});
