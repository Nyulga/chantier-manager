// Tests du composant `Icone` : un pictogramme décoratif, caché des lecteurs d'écran.
import { render } from '@testing-library/react';
import { expect, it } from 'vitest';

import { verifierAccessibilite } from '@/test/verifierAccessibilite';
import { Icone } from './Icone';

it("dessine un pictogramme décoratif, caché des lecteurs d'écran", () => {
  const { container } = render(<Icone nom="adresse" />);

  expect(container.querySelector('svg')).toHaveAttribute('aria-hidden', 'true');
});

it("n'a aucun défaut d'accessibilité détectable par axe", async () => {
  const { container } = render(<Icone nom="plus" />);

  await verifierAccessibilite(container);
});
