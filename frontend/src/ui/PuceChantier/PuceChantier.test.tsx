// Tests du composant `PuceChantier` : l'état d'un chantier, écrit en toutes lettres.
import { render, screen } from '@testing-library/react';
import { expect, it } from 'vitest';

import { verifierAccessibilite } from '../test/verifierAccessibilite';
import { PuceChantier } from './PuceChantier';

it.each([
  ['a-valider', '2 à valider'],
  ['en-retard', 'En retard'],
] as const)('écrit l’état « %s » en toutes lettres', (variante, texte) => {
  render(<PuceChantier variante={variante}>{texte}</PuceChantier>);

  expect(screen.getByText(texte)).toBeVisible();
});

it('n’a aucun défaut d’accessibilité détectable par axe', async () => {
  const { container } = render(<PuceChantier variante="en-retard">En retard</PuceChantier>);

  await verifierAccessibilite(container);
});
