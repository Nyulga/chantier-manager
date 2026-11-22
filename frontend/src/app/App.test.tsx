// Test de l'application assemblée : les fournisseurs et les routes affichent le tableau de bord.
import { render, screen } from '@testing-library/react';
import { http, HttpResponse } from 'msw';
import { expect, it } from 'vitest';

import { installerServeurApi } from '@/ui/test/serveurApiSimule';

import { App } from './App';

const serveur = installerServeurApi();

it('affiche la barre latérale et le tableau de bord au démarrage', async () => {
  serveur.use(
    http.get('/api/chantiers', () => HttpResponse.json([])),
    http.get('/api/etapes/a-valider', () => HttpResponse.json([])),
    http.get('/api/activite', () => HttpResponse.json([])),
  );

  render(<App />);

  expect(screen.getByRole('heading', { level: 1, name: 'Tableau de bord' })).toBeVisible();
  expect(screen.getByText('Chantier Manager')).toBeVisible();
  expect(await screen.findByText('Aucun chantier pour le moment.')).toBeVisible();
});
