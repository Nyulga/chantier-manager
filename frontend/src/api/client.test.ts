// Test du client HTTP : les requêtes partent vers le même domaine, sous le préfixe `/api`.
import { expect, it, vi } from 'vitest';

import { BASE_API, creerClient, MESSAGE_RESEAU } from './client';

/** Description minimale d'un chemin, au format que produit openapi-typescript. */
interface CheminsDeTest {
  '/sante': {
    get: {
      responses: { 200: { content: { 'application/json': { statut: string } } } };
    };
  };
}

it('envoie les requêtes vers le préfixe /api du même domaine', async () => {
  const fetchEspion = vi.fn<typeof fetch>(() => Promise.resolve(Response.json({ statut: 'ok' })));
  vi.stubGlobal('fetch', fetchEspion);

  const reponse = await creerClient<CheminsDeTest>().GET('/sante');

  expect(BASE_API).toBe('/api');
  expect(reponse.data).toEqual({ statut: 'ok' });
  const requete = fetchEspion.mock.calls[0]?.[0];
  expect(requete instanceof Request ? new URL(requete.url).pathname : requete).toBe('/api/sante');
});

it('remplace une panne réseau par un message en français', async () => {
  vi.stubGlobal(
    'fetch',
    vi.fn<typeof fetch>(() => Promise.reject(new TypeError('Failed to fetch'))),
  );

  await expect(creerClient<CheminsDeTest>().GET('/sante')).rejects.toThrow(MESSAGE_RESEAU);
});
