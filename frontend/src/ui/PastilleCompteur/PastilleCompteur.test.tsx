// Tests du composant `PastilleCompteur` : le nombre d'éléments qui attendent une action.
import { render, screen } from '@testing-library/react';
import { expect, it } from 'vitest';

import { verifierAccessibilite } from '../test/verifierAccessibilite';
import { PastilleCompteur } from './PastilleCompteur';

it('affiche le nombre reçu', () => {
  render(<PastilleCompteur valeur={3} />);

  expect(screen.getByText('3')).toBeVisible();
});

it('n’a aucun défaut d’accessibilité détectable par axe', async () => {
  const { container } = render(<PastilleCompteur valeur={3} />);

  await verifierAccessibilite(container);
});
