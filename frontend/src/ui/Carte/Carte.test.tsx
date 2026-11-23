// Tests du composant `Carte` : affiche son contenu, accessible.
import { render, screen } from '@testing-library/react';
import { expect, it } from 'vitest';

import { verifierAccessibilite } from '@/test/verifierAccessibilite';
import { Carte } from './Carte';

it('affiche son contenu', () => {
  render(<Carte>Villa Les Pins</Carte>);

  expect(screen.getByText('Villa Les Pins')).toBeVisible();
});

it("n'a aucun défaut d'accessibilité détectable par axe", async () => {
  const { container } = render(<Carte>Villa Les Pins</Carte>);

  await verifierAccessibilite(container);
});
