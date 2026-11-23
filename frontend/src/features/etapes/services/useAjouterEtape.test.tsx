// Tests du hook `useAjouterEtape` : le corps envoyé, la relecture du chantier et les erreurs.
import { act, waitFor } from '@testing-library/react';
import { http, HttpResponse } from 'msw';
import { expect, it } from 'vitest';

import { chantierDeTest } from '@/test/chantierDeTest';
import { etapeDeTest } from '@/test/etapeDeTest';
import { reponseProbleme } from '@/test/reponseProbleme';
import { afficherHook } from '@/test/afficherHook';
import { installerServeurApi } from '@/test/serveurApiSimule';

import { useAjouterEtape } from './useAjouterEtape';
import { useAvancementChantier } from './useAvancementChantier';

const serveur = installerServeurApi();
const CHANTIER = '0198f1a0-0000-7000-8000-000000000001';

it("envoie le titre à l'API et renvoie l'étape créée", async () => {
  let corps: unknown = null;
  serveur.use(
    http.post(`/api/chantiers/${CHANTIER}/etapes`, async ({ request }) => {
      corps = await request.json();
      return HttpResponse.json(etapeDeTest(), { status: 201 });
    }),
  );
  const { result } = afficherHook(() => useAjouterEtape(CHANTIER));

  act(() => {
    result.current.mutate('Fondations');
  });

  await waitFor(() => {
    expect(result.current.data).toEqual(etapeDeTest());
  });
  expect(corps).toEqual({ titre: 'Fondations' });
});

it("relit l'avancement du chantier après l'ajout : une étape de plus fait baisser le pourcentage", async () => {
  let avancement = 100;
  serveur.use(
    http.get(`/api/chantiers/${CHANTIER}`, () =>
      HttpResponse.json(chantierDeTest({ id: CHANTIER, avancement })),
    ),
    http.post(`/api/chantiers/${CHANTIER}/etapes`, () => {
      avancement = 50;
      return HttpResponse.json(etapeDeTest(), { status: 201 });
    }),
  );
  const { result } = afficherHook(() => ({
    resume: useAvancementChantier(CHANTIER),
    ajout: useAjouterEtape(CHANTIER),
  }));
  await waitFor(() => {
    expect(result.current.resume.data?.avancement).toBe(100);
  });

  act(() => {
    result.current.ajout.mutate('Fondations');
  });

  await waitFor(() => {
    expect(result.current.resume.data?.avancement).toBe(50);
  });
});

it("expose le message de l'API et le champ en cause quand l'ajout est refusé (422)", async () => {
  serveur.use(
    http.post(`/api/chantiers/${CHANTIER}/etapes`, () =>
      reponseProbleme(422, 'Les données envoyées sont invalides.', [
        { champ: 'titre', message: 'Le titre est trop long.' },
      ]),
    ),
  );
  const { result } = afficherHook(() => useAjouterEtape(CHANTIER));

  act(() => {
    result.current.mutate('Fondations');
  });

  await waitFor(() => {
    expect(result.current.error?.message).toBe('Les données envoyées sont invalides.');
  });
  expect(result.current.error?.erreurs).toEqual([
    { champ: 'titre', message: 'Le titre est trop long.' },
  ]);
});

it("expose le message de l'API quand l'ajout entre en conflit (409)", async () => {
  serveur.use(
    http.post(`/api/chantiers/${CHANTIER}/etapes`, () =>
      reponseProbleme(409, "Une autre personne vient d'ajouter une étape : réessaie."),
    ),
  );
  const { result } = afficherHook(() => useAjouterEtape(CHANTIER));

  act(() => {
    result.current.mutate('Fondations');
  });

  await waitFor(() => {
    expect(result.current.error?.message).toBe(
      "Une autre personne vient d'ajouter une étape : réessaie.",
    );
  });
});

it("relit le chantier aussi après un conflit (409) : l'autre ajout doit apparaître", async () => {
  let avancement = 100;
  serveur.use(
    http.get(`/api/chantiers/${CHANTIER}`, () =>
      HttpResponse.json(chantierDeTest({ id: CHANTIER, avancement })),
    ),
    http.post(`/api/chantiers/${CHANTIER}/etapes`, () => {
      avancement = 75;
      return reponseProbleme(409, "Une autre personne vient d'ajouter une étape : réessaie.");
    }),
  );
  const { result } = afficherHook(() => ({
    resume: useAvancementChantier(CHANTIER),
    ajout: useAjouterEtape(CHANTIER),
  }));
  await waitFor(() => {
    expect(result.current.resume.data?.avancement).toBe(100);
  });

  act(() => {
    result.current.ajout.mutate('Fondations');
  });

  await waitFor(() => {
    expect(result.current.resume.data?.avancement).toBe(75);
  });
});
