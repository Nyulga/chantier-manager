// Tests du hook `useChantier` : un chantier par son identifiant, et l'erreur 404 de l'API.
import { renderHook, waitFor } from '@testing-library/react';
import { http, HttpResponse } from 'msw';
import { expect, it } from 'vitest';

import { creerClientRequetes, creerEnveloppe } from '@/test/enveloppeRequetes';
import { reponseProbleme } from '@/test/reponseProbleme';
import { afficherHook } from '@/test/afficherHook';
import { installerServeurApi } from '@/test/serveurApiSimule';

import { chantierDeTest } from '@/test/chantierDeTest';
import { useChantier } from './useChantier';

const serveur = installerServeurApi();

it('renvoie le chantier demandé', async () => {
  const chantier = chantierDeTest();
  serveur.use(http.get(`/api/chantiers/${chantier.id}`, () => HttpResponse.json(chantier)));

  const { result } = afficherHook(() => useChantier(chantier.id));

  await waitFor(() => {
    expect(result.current.data).toEqual(chantier);
  });
});

it("expose le message de l'API et reconnaît un chantier introuvable (404)", async () => {
  serveur.use(
    http.get('/api/chantiers/inconnu', () => reponseProbleme(404, 'Chantier introuvable.')),
  );

  const { result } = afficherHook(() => useChantier('inconnu'));

  await waitFor(() => {
    expect(result.current.error?.message).toBe('Chantier introuvable.');
  });
  expect(result.current.error?.introuvable).toBe(true);
});

it('ne rejoue pas un chantier introuvable, mais rejoue une panne passagère', async () => {
  const chantier = chantierDeTest();
  let appels404 = 0;
  let appelsPanne = 0;
  serveur.use(
    http.get('/api/chantiers/inconnu', () => {
      appels404 += 1;
      return reponseProbleme(404, 'Chantier introuvable.');
    }),
    http.get(`/api/chantiers/${chantier.id}`, () => {
      appelsPanne += 1;
      return appelsPanne === 1
        ? reponseProbleme(503, 'Service indisponible.')
        : HttpResponse.json(chantier);
    }),
  );
  const wrapper = creerEnveloppe(creerClientRequetes());

  const introuvable = renderHook(() => useChantier('inconnu'), { wrapper });
  const panne = renderHook(() => useChantier(chantier.id), { wrapper });

  await waitFor(() => {
    expect(introuvable.result.current.isError).toBe(true);
  });
  await waitFor(() => {
    expect(panne.result.current.data).toEqual(chantier);
  });
  expect(appels404).toBe(1);
  expect(appelsPanne).toBe(2);
});

it('ne confond pas le chantier « liste » avec la liste des chantiers en cache', async () => {
  const client = creerClientRequetes();
  client.setQueryData(['chantiers', 'liste'], []);
  const chantier = chantierDeTest({ id: 'liste' });
  serveur.use(http.get('/api/chantiers/liste', () => HttpResponse.json(chantier)));

  const { result } = renderHook(() => useChantier('liste'), { wrapper: creerEnveloppe(client) });

  // Avant la réponse de l'API, rien ne doit être pris pour le chantier (surtout pas le tableau).
  expect(result.current.data).toBeUndefined();
  await waitFor(() => {
    expect(result.current.data).toEqual(chantier);
  });
});
