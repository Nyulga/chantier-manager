// Tests de l'en-tête `X-Profil` : le client l'envoie avec chaque requête (MSW simule l'API).
import { http, HttpResponse } from 'msw';
import { setupServer } from 'msw/node';
import { afterAll, afterEach, beforeAll, expect, it } from 'vitest';

import { creerClientApi } from './client';
import { enregistrerProfil } from './profil';

const serveur = setupServer();

beforeAll(() => {
  serveur.listen({ onUnhandledFrame: 'error' });
});
afterEach(() => {
  serveur.resetHandlers();
  localStorage.clear();
});
afterAll(() => {
  serveur.close();
});

/** Appelle l'API simulée et renvoie la valeur de l'en-tête `X-Profil` que le serveur a reçue. */
async function profilEnvoye(): Promise<string | null> {
  let recu: string | null = null;
  serveur.use(
    http.get('/api/health', ({ request }) => {
      recu = request.headers.get('X-Profil');
      return HttpResponse.json({ statut: 'ok' });
    }),
  );

  await creerClientApi().GET('/health');

  return recu;
}

it('envoie « chef » par défaut', async () => {
  expect(await profilEnvoye()).toBe('chef');
});

it('envoie le profil courant à chaque requête, même après un changement', async () => {
  const client = creerClientApi();
  serveur.use(
    http.get('/api/health', ({ request }) =>
      HttpResponse.json(
        { statut: 'ok' },
        { headers: { 'X-Eco': request.headers.get('X-Profil') ?? '' } },
      ),
    ),
  );

  enregistrerProfil('ouvrier');
  const premiere = await client.GET('/health');
  enregistrerProfil('chef');
  const seconde = await client.GET('/health');

  expect(premiere.response.headers.get('X-Eco')).toBe('ouvrier');
  expect(seconde.response.headers.get('X-Eco')).toBe('chef');
});
