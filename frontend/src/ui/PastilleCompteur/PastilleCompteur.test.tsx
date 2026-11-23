// Tests du composant `PastilleCompteur` : le nombre d'éléments qui attendent une action.
import { render, screen } from '@testing-library/react';
import { expect, it } from 'vitest';

import { verifierAccessibilite } from '@/test/verifierAccessibilite';
import { PastilleCompteur } from './PastilleCompteur';

it('affiche le nombre reçu', () => {
  render(<PastilleCompteur valeur={3} />);

  expect(screen.getByText('3')).toBeVisible();
});

it('ajoute « + » quand le nombre est un minimum : la liste est coupée', () => {
  render(<PastilleCompteur valeur={50} auMoins />);

  expect(screen.getByText('50+')).toBeVisible();
});

it("n'a aucun défaut d'accessibilité détectable par axe", async () => {
  const { container } = render(<PastilleCompteur valeur={3} />);

  await verifierAccessibilite(container);
});
