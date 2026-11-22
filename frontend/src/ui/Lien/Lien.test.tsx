// Tests du composant `Lien` : navigation interne via react-router, accessible.
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router';
import { expect, it } from 'vitest';

import { verifierAccessibilite } from '../test/verifierAccessibilite';
import { Lien } from './Lien';

function afficher() {
  return render(
    <MemoryRouter>
      <Lien vers="/chantiers/42">Voir le chantier</Lien>
    </MemoryRouter>,
  );
}

it('affiche un lien vers l’adresse demandée', () => {
  afficher();

  expect(screen.getByRole('link', { name: 'Voir le chantier' })).toHaveAttribute(
    'href',
    '/chantiers/42',
  );
});

it('n’a aucun défaut d’accessibilité détectable par axe', async () => {
  const { container } = afficher();

  await verifierAccessibilite(container);
});
