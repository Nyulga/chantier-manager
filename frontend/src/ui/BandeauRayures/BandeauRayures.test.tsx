// Tests du composant `BandeauRayures` : un repère décoratif, sans contenu pour les lecteurs d'écran.
import { render } from '@testing-library/react';
import { expect, it } from 'vitest';

import { verifierAccessibilite } from '../test/verifierAccessibilite';
import { BandeauRayures } from './BandeauRayures';

it('est décoratif : caché des lecteurs d’écran', () => {
  const { container } = render(<BandeauRayures />);

  expect(container.firstElementChild).toHaveAttribute('aria-hidden', 'true');
});

it('n’a aucun défaut d’accessibilité détectable par axe', async () => {
  const { container } = render(<BandeauRayures />);

  await verifierAccessibilite(container);
});
