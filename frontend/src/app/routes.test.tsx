// Tests de la table des routes : l'adresse `/` mène à la page d'accueil.
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router';
import { expect, it } from 'vitest';

import { RoutesApplication } from './routes';

it("affiche la page d'accueil à l'adresse racine", () => {
  render(
    <MemoryRouter initialEntries={['/']}>
      <RoutesApplication />
    </MemoryRouter>,
  );

  expect(screen.getByRole('heading', { level: 1, name: 'Chantier Manager' })).toBeVisible();
});
