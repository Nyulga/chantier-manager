// Tests des `Colonnes` : la colonne principale puis la colonne latérale, dans cet ordre de lecture.
import { render, screen } from '@testing-library/react';
import { expect, it } from 'vitest';

import { verifierAccessibilite } from '../test/verifierAccessibilite';
import { Colonnes } from './Colonnes';

function afficher() {
  return render(<Colonnes laterale={<p>Latérale</p>}>Principale</Colonnes>);
}

it('affiche la colonne principale puis la colonne latérale', () => {
  const { container } = afficher();

  expect(screen.getByText('Principale')).toBeVisible();
  expect(screen.getByText('Latérale')).toBeVisible();
  expect(container.textContent).toBe('PrincipaleLatérale');
});

it('n’a aucun défaut d’accessibilité détectable par axe', async () => {
  const { container } = afficher();

  await verifierAccessibilite(container);
});
