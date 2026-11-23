// Tests du composant `Avatar` : les initiales dans un cercle, décoratives à côté du nom.
import { render, screen } from '@testing-library/react';
import { expect, it } from 'vitest';

import { verifierAccessibilite } from '@/test/verifierAccessibilite';
import { Avatar } from './Avatar';

it('affiche les initiales, sans les annoncer : le nom est écrit à côté', () => {
  render(<Avatar initiales="CH" />);

  expect(screen.getByText('CH')).toHaveAttribute('aria-hidden', 'true');
});

it("n'a aucun défaut d'accessibilité détectable par axe", async () => {
  const { container } = render(<Avatar initiales="CH" />);

  await verifierAccessibilite(container);
});
