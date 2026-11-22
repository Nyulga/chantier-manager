// Test de l'application assemblée : les fournisseurs et les routes affichent l'accueil.
import { render, screen } from '@testing-library/react';
import { expect, it } from 'vitest';

import { App } from './App';

it("affiche la page d'accueil au démarrage", () => {
  render(<App />);

  expect(screen.getByRole('heading', { level: 1, name: 'Chantier Manager' })).toBeVisible();
});
