// Tests du hook `useTransitionEtape` : le corps envoyé, la relecture des données (succès comme erreur) et les erreurs de l'API.
import { act, renderHook, waitFor } from '@testing-library/react';
import { http, HttpResponse } from 'msw';
import { expect, it, vi } from 'vitest';

import { creerClientRequetes, creerEnveloppe } from '@/api/test/enveloppeRequetes';
import { installerServeurApi } from '@/api/test/serveurApiSimule';

import { etapeDeTest } from './etapeDeTest';
import { useEtapes } from './useEtapes';
import { useTransitionEtape } from './useTransitionEtape';

const serveur = installerServeurApi();
const ETAPE = etapeDeTest({ statut: 'en_cours' });

it('envoie l’action et le commentaire à l’API', async () => {
  let corps: unknown = null;
  serveur.use(
    http.post(`/api/etapes/${ETAPE.id}/transitions`, async ({ request }) => {
      corps = await request.json();
      return HttpResponse.json(ETAPE);
    }),
  );
  const { result } = renderHook(() => useTransitionEtape(), {
    wrapper: creerEnveloppe(creerClientRequetes()),
  });

  act(() => {
    result.current.mutate({
      etapeId: ETAPE.id,
      chantierId: ETAPE.chantier_id,
      action: 'refuser',
      commentaire: 'Mal fini',
    });
  });

  await waitFor(() => {
    expect(result.current.data).toEqual(ETAPE);
  });
  expect(corps).toEqual({ action: 'refuser', commentaire: 'Mal fini' });
});

/** Sonde : les étapes du chantier et la transition, dans le même cache, comme sur la page. */
function useSonde() {
  return { etapes: useEtapes(ETAPE.chantier_id), transition: useTransitionEtape() };
}

/** Répond à la lecture des étapes en comptant les appels : le contenu change à chaque lecture. */
function simulerLectureEtapes() {
  const lectures = { nombre: 0 };
  serveur.use(
    http.get(`/api/chantiers/${ETAPE.chantier_id}/etapes`, () => {
      lectures.nombre += 1;
      return HttpResponse.json([etapeDeTest({ version: lectures.nombre })]);
    }),
  );
  return lectures;
}

it('relit les étapes après une transition réussie', async () => {
  const lectures = simulerLectureEtapes();
  serveur.use(http.post(`/api/etapes/${ETAPE.id}/transitions`, () => HttpResponse.json(ETAPE)));
  const { result } = renderHook(() => useSonde(), {
    wrapper: creerEnveloppe(creerClientRequetes()),
  });
  await waitFor(() => {
    expect(result.current.etapes.data?.[0]?.version).toBe(1);
  });

  act(() => {
    result.current.transition.mutate({
      etapeId: ETAPE.id,
      chantierId: ETAPE.chantier_id,
      action: 'valider',
    });
  });

  await waitFor(() => {
    expect(result.current.etapes.data?.[0]?.version).toBe(2);
  });
  expect(lectures.nombre).toBe(2);
});

it('relit les étapes aussi après un conflit (409) : l’écran n’est pas périmé', async () => {
  const lectures = simulerLectureEtapes();
  serveur.use(
    http.post(`/api/etapes/${ETAPE.id}/transitions`, () =>
      HttpResponse.json(
        { status: 409, detail: 'Cette étape a déjà changé de statut.' },
        { status: 409, headers: { 'Content-Type': 'application/problem+json' } },
      ),
    ),
  );
  const { result } = renderHook(() => useSonde(), {
    wrapper: creerEnveloppe(creerClientRequetes()),
  });
  await waitFor(() => {
    expect(result.current.etapes.data?.[0]?.version).toBe(1);
  });

  act(() => {
    result.current.transition.mutate({
      etapeId: ETAPE.id,
      chantierId: ETAPE.chantier_id,
      action: 'valider',
    });
  });

  await waitFor(() => {
    expect(result.current.etapes.data?.[0]?.version).toBe(2);
  });
  expect(result.current.transition.error?.message).toBe('Cette étape a déjà changé de statut.');
  expect(lectures.nombre).toBe(2);
});

it('expose le message de l’API quand la transition est refusée (422)', async () => {
  serveur.use(
    http.post(`/api/etapes/${ETAPE.id}/transitions`, () =>
      HttpResponse.json(
        { status: 422, detail: 'Le commentaire du refus est obligatoire.' },
        { status: 422, headers: { 'Content-Type': 'application/problem+json' } },
      ),
    ),
  );
  const { result } = renderHook(() => useTransitionEtape(), {
    wrapper: creerEnveloppe(creerClientRequetes()),
  });

  act(() => {
    result.current.mutate({ etapeId: ETAPE.id, chantierId: ETAPE.chantier_id, action: 'refuser' });
  });

  await waitFor(() => {
    expect(result.current.error?.message).toBe('Le commentaire du refus est obligatoire.');
  });
});

it('invalide aussi les étapes à valider et l’activité du tableau de bord', async () => {
  serveur.use(http.post(`/api/etapes/${ETAPE.id}/transitions`, () => HttpResponse.json(ETAPE)));
  const client = creerClientRequetes();
  const invalider = vi.spyOn(client, 'invalidateQueries');
  const { result } = renderHook(() => useTransitionEtape(), { wrapper: creerEnveloppe(client) });

  act(() => {
    result.current.mutate({
      etapeId: ETAPE.id,
      chantierId: ETAPE.chantier_id,
      action: 'valider',
    });
  });

  await waitFor(() => {
    expect(invalider).toHaveBeenCalledWith({ queryKey: ['etapes', 'a-valider'] });
  });
  expect(invalider).toHaveBeenCalledWith({ queryKey: ['activite'] });
});
