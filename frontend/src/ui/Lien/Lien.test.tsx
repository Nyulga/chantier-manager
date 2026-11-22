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

it.each(['principal', 'secondaire'] as const)(
  'reste un lien quand il a l’apparence d’un bouton %s',
  (variante) => {
    render(
      <MemoryRouter>
        <Lien vers="/chantiers/nouveau" variante={variante}>
          Nouveau chantier
        </Lien>
      </MemoryRouter>,
    );

    expect(screen.getByRole('link', { name: 'Nouveau chantier' })).toHaveAttribute(
      'href',
      '/chantiers/nouveau',
    );
  },
);

it('peut porter un nom accessible plus précis que son libellé visible', () => {
  render(
    <MemoryRouter>
      <Lien vers="/chantiers/42" variante="secondaire" libelleAccessible="Examiner : Fondations">
        Examiner
      </Lien>
    </MemoryRouter>,
  );

  expect(screen.getByRole('link', { name: 'Examiner : Fondations' })).toBeVisible();
});
