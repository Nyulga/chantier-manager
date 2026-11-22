// Tests du composant `Page` : zone principale unique de l'écran, accessible.
import { render, screen } from '@testing-library/react';

import { expect, it } from 'vitest';

import { verifierAccessibilite } from '../test/verifierAccessibilite';
import { Page } from './Page';

it('affiche son contenu dans la zone principale de la page', () => {
  render(<Page>Contenu de la page</Page>);

  expect(screen.getByRole('main')).toHaveTextContent('Contenu de la page');
});

it("n'a aucun défaut d'accessibilité détectable par axe", async () => {
  const { container } = render(<Page>Contenu de la page</Page>);

  await verifierAccessibilite(container);
});
