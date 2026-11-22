// Tests de la `Grille` : chaque enfant devient un élément de liste.
import { render, screen } from '@testing-library/react';
import { expect, it } from 'vitest';

import { verifierAccessibilite } from '../test/verifierAccessibilite';
import { Grille } from './Grille';

function afficher() {
  return render(
    <Grille>
      <p>Un</p>
      <p>Deux</p>
    </Grille>,
  );
}

it('range chaque enfant dans un élément de liste', () => {
  afficher();

  expect(screen.getAllByRole('listitem')).toHaveLength(2);
});

it('n’a aucun défaut d’accessibilité détectable par axe', async () => {
  const { container } = afficher();

  await verifierAccessibilite(container);
});
