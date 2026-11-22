// Tests du composant `MentionBientot` : la mention visible d'une fonction pas encore disponible.
import { render, screen } from '@testing-library/react';
import { expect, it } from 'vitest';

import { verifierAccessibilite } from '../test/verifierAccessibilite';
import { MentionBientot } from './MentionBientot';

it('écrit « Bientôt » en toutes lettres', () => {
  render(<MentionBientot />);

  expect(screen.getByText('Bientôt')).toBeVisible();
});

it('n’a aucun défaut d’accessibilité détectable par axe', async () => {
  const { container } = render(<MentionBientot />);

  await verifierAccessibilite(container);
});
