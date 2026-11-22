// Tests du hook `useCreerChantier` : le corps envoyé, l'invalidation de la liste et les erreurs.
import { act, renderHook, waitFor } from '@testing-library/react';
import { http, HttpResponse } from 'msw';
import { expect, it, vi } from 'vitest';

import { creerClientRequetes, creerEnveloppe } from '@/api/test/enveloppeRequetes';
import { installerServeurApi } from '@/api/test/serveurApiSimule';

import { chantierDeTest } from './chantierDeTest';
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

it('envoie le chantier à l’API sous la forme attendue et renvoie le chantier créé', async () => {
  const cree = chantierDeTest();
  let corps: unknown = null;
  serveur.use(
    http.post('/api/chantiers', async ({ request }) => {
      corps = await request.json();
      return HttpResponse.json(cree, { status: 201 });
    }),
  );
  const { result } = renderHook(() => useCreerChantier(), {
    wrapper: creerEnveloppe(creerClientRequetes()),
  });

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

it('invalide la liste des chantiers après la création', async () => {
  serveur.use(
    http.post('/api/chantiers', () => HttpResponse.json(chantierDeTest(), { status: 201 })),
  );
  const client = creerClientRequetes();
  const invalider = vi.spyOn(client, 'invalidateQueries');
  const { result } = renderHook(() => useCreerChantier(), { wrapper: creerEnveloppe(client) });

  act(() => {
    result.current.mutate(SAISIE);
  });

  await waitFor(() => {
    expect(invalider).toHaveBeenCalledWith({ queryKey: ['chantiers', 'liste'] });
  });
});

it('expose le message de l’API quand la création est refusée', async () => {
  serveur.use(
    http.post('/api/chantiers', () =>
      HttpResponse.json(
        { status: 403, detail: 'Seul un chef peut créer un chantier.' },
        { status: 403, headers: { 'Content-Type': 'application/problem+json' } },
      ),
    ),
  );
  const { result } = renderHook(() => useCreerChantier(), {
    wrapper: creerEnveloppe(creerClientRequetes()),
  });

  act(() => {
    result.current.mutate(SAISIE);
  });

  await waitFor(() => {
    expect(result.current.error?.message).toBe('Seul un chef peut créer un chantier.');
  });
});
