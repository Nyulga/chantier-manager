// Tests du hook `useTransitionEtape` : le corps envoyé, la relecture des données (succès comme erreur) et les erreurs de l'API.
import { useQuery } from '@tanstack/react-query';
import { act, waitFor } from '@testing-library/react';
import { http, HttpResponse } from 'msw';
import { expect, it } from 'vitest';

import { clesRequetes } from '@/api/clesRequetes';
import { creerClientApi } from '@/api/client';
import { donneesOuErreur } from '@/api/erreurApi';
import { etapeDeTest } from '@/test/etapeDeTest';
import { reponseProbleme } from '@/test/reponseProbleme';
import { afficherHook } from '@/test/afficherHook';
import { installerServeurApi } from '@/test/serveurApiSimule';

import { useEtapes } from './useEtapes';
import { useTransitionEtape } from './useTransitionEtape';

const serveur = installerServeurApi();
const ETAPE = etapeDeTest({ statut: 'en_cours', version: 4 });
const DEMANDE = {
  etapeId: ETAPE.id,
  chantierId: ETAPE.chantier_id,
  action: 'valider',
  version: ETAPE.version,
} as const;

it("envoie l'action, le commentaire et la version affichée à l'API", async () => {
  let corps: unknown = null;
  serveur.use(
    http.post(`/api/etapes/${ETAPE.id}/transitions`, async ({ request }) => {
      corps = await request.json();
      return HttpResponse.json(ETAPE);
    }),
  );
  const { result } = afficherHook(() => useTransitionEtape());

  act(() => {
    result.current.mutate({ ...DEMANDE, action: 'refuser', commentaire: 'Mal fini' });
  });

  await waitFor(() => {
    expect(result.current.data).toEqual(ETAPE);
  });
  expect(corps).toEqual({ action: 'refuser', commentaire: 'Mal fini', version: 4 });
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
  const { result } = afficherHook(() => useSonde());
  await waitFor(() => {
    expect(result.current.etapes.data?.[0]?.version).toBe(1);
  });

  act(() => {
    result.current.transition.mutate(DEMANDE);
  });

  await waitFor(() => {
    expect(result.current.etapes.data?.[0]?.version).toBe(2);
  });
  expect(lectures.nombre).toBe(2);
});

it("relit les étapes aussi après un conflit de version (409) : l'écran n'est pas périmé", async () => {
  const lectures = simulerLectureEtapes();
  serveur.use(
    http.post(`/api/etapes/${ETAPE.id}/transitions`, () =>
      reponseProbleme(409, 'Cette étape a déjà changé de statut.'),
    ),
  );
  const { result } = afficherHook(() => useSonde());
  await waitFor(() => {
    expect(result.current.etapes.data?.[0]?.version).toBe(1);
  });

  act(() => {
    result.current.transition.mutate(DEMANDE);
  });

  await waitFor(() => {
    expect(result.current.etapes.data?.[0]?.version).toBe(2);
  });
  expect(result.current.transition.error?.message).toBe('Cette étape a déjà changé de statut.');
  expect(lectures.nombre).toBe(2);
});

it("expose le message de l'API et le champ en cause quand le refus est invalide (422)", async () => {
  serveur.use(
    http.post(`/api/etapes/${ETAPE.id}/transitions`, () =>
      reponseProbleme(422, 'Les données envoyées sont invalides.', [
        { champ: 'commentaire', message: 'Le commentaire du refus est obligatoire.' },
      ]),
    ),
  );
  const { result } = afficherHook(() => useTransitionEtape());

  act(() => {
    result.current.mutate({ ...DEMANDE, action: 'refuser' });
  });

  await waitFor(() => {
    expect(result.current.error?.erreurs).toEqual([
      { champ: 'commentaire', message: 'Le commentaire du refus est obligatoire.' },
    ]);
  });
});

/** Sonde : les lectures du tableau de bord (étapes à valider, activité), qui partagent le cache. */
function useSondeTableauDeBord() {
  const aValider = useQuery({
    queryKey: clesRequetes.etapesAValider(),
    queryFn: async () => donneesOuErreur(await creerClientApi().GET('/etapes/a-valider')),
  });
  const activite = useQuery({
    queryKey: clesRequetes.activite(),
    queryFn: async () => donneesOuErreur(await creerClientApi().GET('/activite')),
  });
  return { aValider, activite, transition: useTransitionEtape() };
}

it("relit aussi les étapes à valider et l'activité du tableau de bord", async () => {
  const lectures = { aValider: 0, activite: 0 };
  serveur.use(
    http.post(`/api/etapes/${ETAPE.id}/transitions`, () => HttpResponse.json(ETAPE)),
    http.get('/api/etapes/a-valider', () => {
      lectures.aValider += 1;
      return HttpResponse.json([]);
    }),
    http.get('/api/activite', () => {
      lectures.activite += 1;
      return HttpResponse.json([]);
    }),
  );
  const { result } = afficherHook(() => useSondeTableauDeBord());
  await waitFor(() => {
    expect(result.current.aValider.isSuccess && result.current.activite.isSuccess).toBe(true);
  });

  act(() => {
    result.current.transition.mutate(DEMANDE);
  });

  await waitFor(() => {
    expect(lectures).toEqual({ aValider: 2, activite: 2 });
  });
});
