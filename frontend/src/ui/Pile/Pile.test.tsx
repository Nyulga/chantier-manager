// Tests du composant `Pile` : empile ses enfants dans l'ordre, accessible.
import { render, screen } from '@testing-library/react';
import { expect, it } from 'vitest';

import { verifierAccessibilite } from '@/test/verifierAccessibilite';
import { Pile } from './Pile';

it("affiche ses enfants dans l'ordre", () => {
  render(
    <Pile>
      <p>Premier</p>
      <p>Second</p>
    </Pile>,
  );

  const [premier, second] = screen.getAllByText(/^(Premier|Second)$/);

  expect(premier).toHaveTextContent('Premier');
  expect(second).toHaveTextContent('Second');
});

it.each(['moyen', 'grand'] as const)(
  "l'espacement %s n'a aucun défaut d'accessibilité détectable par axe",
  async (espace) => {
    const { container } = render(
      <Pile espace={espace}>
        <p>Contenu</p>
      </Pile>,
    );

    await verifierAccessibilite(container);
  },
);
