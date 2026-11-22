// Test de l'application assemblée : les fournisseurs et les routes affichent la liste des chantiers.
import { render, screen } from '@testing-library/react';
import { http, HttpResponse } from 'msw';
import { expect, it } from 'vitest';

import { installerServeurApi } from '@/ui/test/serveurApiSimule';

import { App } from './App';

const serveur = installerServeurApi();

it('affiche l’en-tête et la liste des chantiers au démarrage', async () => {
  serveur.use(http.get('/api/chantiers', () => HttpResponse.json([])));

  render(<App />);

  expect(screen.getByRole('heading', { level: 1, name: 'Chantier Manager' })).toBeVisible();
  expect(await screen.findByText('Aucun chantier pour le moment.')).toBeVisible();
});
