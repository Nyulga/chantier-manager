// Tests du point d'entrée : montage dans `#root`, et erreur claire si l'élément est absent.
import { screen } from '@testing-library/react';
import { http, HttpResponse } from 'msw';
import { afterEach, expect, it, vi } from 'vitest';

import { installerServeurApi } from '@/ui/test/serveurApiSimule';

const serveur = installerServeurApi();

afterEach(() => {
  document.body.innerHTML = '';
  vi.resetModules();
});

it("monte l'application dans l'élément racine de la page", async () => {
  // Le tableau de bord interroge l'API au montage : on la simule pour ne jamais sortir sur le réseau.
  serveur.use(
    http.get('/api/chantiers', () => HttpResponse.json([])),
    http.get('/api/etapes/a-valider', () => HttpResponse.json([])),
    http.get('/api/activite', () => HttpResponse.json([])),
  );
  document.body.innerHTML = '<div id="root"></div>';

  await import('./main');

  expect(await screen.findByRole('heading', { level: 1, name: 'Tableau de bord' })).toBeVisible();
});

it("échoue avec un message clair si l'élément racine est absent", async () => {
  await expect(import('./main')).rejects.toThrow("L'élément #root est introuvable");
});
