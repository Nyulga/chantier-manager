// Tests de la `BarreLaterale` : logo, navigation principale et pied de barre.
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router';
import { expect, it } from 'vitest';

import { ElementNavigation } from '../ElementNavigation/ElementNavigation';
import { verifierAccessibilite } from '@/test/verifierAccessibilite';
import { BarreLaterale } from './BarreLaterale';

function afficher() {
  return render(
    <MemoryRouter>
      <BarreLaterale
        navigation={
          <ElementNavigation vers="/" exact icone="tableau-de-bord">
            Tableau de bord
          </ElementNavigation>
        }
        pied={<p>Pied de barre</p>}
      />
    </MemoryRouter>,
  );
}

it('affiche le logo, la navigation principale et le pied', () => {
  afficher();

  expect(screen.getByText('Chantier Manager')).toBeVisible();
  expect(screen.getByRole('navigation', { name: 'Navigation principale' })).toBeVisible();
  expect(screen.getByRole('link', { name: 'Tableau de bord' })).toBeVisible();
  expect(screen.getByText('Pied de barre')).toBeVisible();
});

it("n'a aucun défaut d'accessibilité détectable par axe", async () => {
  const { container } = afficher();

  await verifierAccessibilite(container);
});
