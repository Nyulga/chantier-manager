// Tests du composant `Alerte` : une erreur est annoncée tout de suite, et nommée en toutes lettres.
import { render, screen } from '@testing-library/react';
import { expect, it } from 'vitest';

import { verifierAccessibilite } from '@/test/verifierAccessibilite';

import { Alerte } from './Alerte';

it('annonce une erreur avec role="alert" et la nomme en toutes lettres', () => {
  render(<Alerte>Le serveur ne répond pas.</Alerte>);

  const alerte = screen.getByRole('alert');

  expect(alerte).toHaveTextContent('Erreur');
  expect(alerte).toHaveTextContent('Le serveur ne répond pas.');
});

it("n'a aucun défaut d'accessibilité détectable par axe", async () => {
  const { container } = render(<Alerte>Message</Alerte>);

  await verifierAccessibilite(container);
});
