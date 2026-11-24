// Suite de tests commune aux hooks de lecture : ils suivent tous la règle de nouvelle tentative de `src/api/reessai.ts`.
import { renderHook, waitFor } from '@testing-library/react';
import { http, HttpResponse, type JsonBodyType } from 'msw';
import { expect, it } from 'vitest';

import { creerClientRequetes, creerEnveloppe } from './enveloppeRequetes';
import { reponseProbleme } from './reponseProbleme';
import type { installerServeurApi } from './serveurApiSimule';

type Parametres = {
  readonly serveur: ReturnType<typeof installerServeurApi>;
  /** Adresse que le hook lit, par exemple `/api/chantiers`. */
  readonly chemin: string;
  /** Réponse réussie de l'API. */
  readonly corps: JsonBodyType;
  /** Le hook testé, appelé tel quel : seul son effet sur le cache est observé. */
  readonly utiliser: () => unknown;
};

/**
 * Prouve que le hook ne rejoue pas un refus de l'API et rejoue une panne. La règle vient du client
 * de requêtes (le cache de test reprend celui de l'application) : le test échoue si un hook la
 * remplace par une autre. On lit l'état de la requête dans le cache, car certains hooks (le compteur
 * de la navigation) ne rendent que leur valeur.
 */
export function testerReessai({ serveur, chemin, corps, utiliser }: Parametres) {
  function observer() {
    const client = creerClientRequetes();
    renderHook(utiliser, { wrapper: creerEnveloppe(client) });
    return client.getQueryCache();
  }

  it.each([403, 404])(
    "ne rejoue pas une requête que l'API refuse (%i) : la réponse ne changerait pas",
    async (statut) => {
      let appels = 0;
      serveur.use(
        http.get(chemin, () => {
          appels += 1;
          return reponseProbleme(statut, 'Refusé.');
        }),
      );

      const cache = observer();

      // L'état « erreur » n'est atteint qu'une fois les nouvelles tentatives épuisées.
      await waitFor(() => {
        expect(cache.getAll()[0]?.state.status).toBe('error');
      });
      expect(appels).toBe(1);
    },
  );

  it('rejoue une panne du serveur (503) et réussit à la tentative suivante', async () => {
    let appels = 0;
    serveur.use(
      http.get(chemin, () => {
        appels += 1;
        return appels === 1 ? reponseProbleme(503, 'Indisponible.') : HttpResponse.json(corps);
      }),
    );

    const cache = observer();

    await waitFor(() => {
      expect(cache.getAll()[0]?.state.status).toBe('success');
    });
    expect(appels).toBe(2);
  });
}
