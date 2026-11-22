// Tests de la page d'accueil : titre du produit, emplacement de l'état de l'API et accessibilité.
import { render, screen } from '@testing-library/react';

import { expect, it } from 'vitest';

import { verifierAccessibilite } from '@/ui/test/verifierAccessibilite';

import { PageAccueil } from './PageAccueil';

it("affiche le nom de l'application en titre principal", () => {
  render(<PageAccueil />);

  expect(screen.getByRole('heading', { level: 1, name: 'Chantier Manager' })).toBeVisible();
});

it("réserve un emplacement pour l'état de l'API, en français", () => {
  render(<PageAccueil />);

  expect(screen.getByText(/État de l’API/)).toBeVisible();
});

it("n'a aucun défaut d'accessibilité détectable par axe", async () => {
  const { container } = render(<PageAccueil />);

  await verifierAccessibilite(container);
});
