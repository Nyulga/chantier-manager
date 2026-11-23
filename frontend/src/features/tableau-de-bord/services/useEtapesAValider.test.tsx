// Tests du hook `useEtapesAValider` : la liste vient de l'API, avec l'indication « liste coupée ».
import { waitFor } from '@testing-library/react';
import { http, HttpResponse } from 'msw';
import { expect, it } from 'vitest';

import { etapeAValiderDeTest } from '@/test/etapeAValiderDeTest';
import { reponseProbleme } from '@/test/reponseProbleme';
import { afficherHook } from '@/test/afficherHook';
import { installerServeurApi } from '@/test/serveurApiSimule';

import { useEtapesAValider } from './useEtapesAValider';

const serveur = installerServeurApi();

function afficher(autorisee = true) {
  return afficherHook(() => useEtapesAValider(autorisee));
}

it("renvoie les étapes à valider de l'API, dans son ordre", async () => {
  const etapes = [etapeAValiderDeTest(), etapeAValiderDeTest({ id: 'autre', titre: 'Faïence' })];
  serveur.use(http.get('/api/etapes/a-valider', () => HttpResponse.json(etapes)));

  const { result } = afficher();

  await waitFor(() => {
    expect(result.current.data?.etapes).toEqual(etapes);
  });
  expect(result.current.data?.tronquee).toBe(false);
});

it("signale une liste coupée quand l'en-tête X-Liste-Tronquee vaut « true »", async () => {
  serveur.use(
    http.get('/api/etapes/a-valider', () =>
      HttpResponse.json([etapeAValiderDeTest()], { headers: { 'X-Liste-Tronquee': 'true' } }),
    ),
  );

  const { result } = afficher();

  await waitFor(() => {
    expect(result.current.data?.tronquee).toBe(true);
  });
});

it("ne signale pas de liste coupée quand l'en-tête vaut « false »", async () => {
  serveur.use(
    http.get('/api/etapes/a-valider', () =>
      HttpResponse.json([], { headers: { 'X-Liste-Tronquee': 'false' } }),
    ),
  );

  const { result } = afficher();

  await waitFor(() => {
    expect(result.current.isSuccess).toBe(true);
  });
  expect(result.current.data?.tronquee).toBe(false);
});

it("n'envoie aucune requête quand l'API n'annonce pas le droit de lister", () => {
  let appels = 0;
  serveur.use(
    http.get('/api/etapes/a-valider', () => {
      appels += 1;
      return HttpResponse.json([]);
    }),
  );

  const { result } = afficher(false);

  expect(result.current.data).toBeUndefined();
  expect(result.current.fetchStatus).toBe('idle');
  expect(appels).toBe(0);
});

it("ne rejoue pas un refus de l'API (403), mais rejoue une panne passagère", async () => {
  let refus = 0;
  let pannes = 0;
  const etapes = [etapeAValiderDeTest()];
  serveur.use(
    http.get('/api/etapes/a-valider', () => {
      pannes += 1;
      return pannes === 1
        ? reponseProbleme(503, 'Service indisponible.')
        : HttpResponse.json(etapes);
    }),
  );

  const panne = afficher();
  await waitFor(() => {
    expect(panne.result.current.data?.etapes).toEqual(etapes);
  });
  serveur.use(
    http.get('/api/etapes/a-valider', () => {
      refus += 1;
      return reponseProbleme(403, 'Action réservée à un chef.');
    }),
  );
  const refuse = afficher();

  await waitFor(() => {
    expect(refuse.result.current.error?.message).toBe('Action réservée à un chef.');
  });
  expect(pannes).toBe(2);
  expect(refus).toBe(1);
});

it("expose le message de l'API quand elle répond par une erreur", async () => {
  serveur.use(
    http.get('/api/etapes/a-valider', () => reponseProbleme(403, 'Action réservée à un chef.')),
  );

  const { result } = afficher();

  await waitFor(() => {
    expect(result.current.error?.message).toBe('Action réservée à un chef.');
  });
});
