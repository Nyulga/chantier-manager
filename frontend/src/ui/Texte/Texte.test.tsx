// Tests du composant `Texte` : chaque variante affiche son contenu et reste accessible.
import { render, screen } from '@testing-library/react';

import { expect, it } from 'vitest';

import { verifierAccessibilite } from '../test/verifierAccessibilite';
import { Texte } from './Texte';

it('affiche son contenu avec la variante courante par défaut', () => {
  render(<Texte>Bienvenue sur le chantier</Texte>);

  expect(screen.getByText('Bienvenue sur le chantier')).toBeVisible();
});

it.each(['courant', 'secondaire', 'etiquette', 'donnee'] as const)(
  'affiche son contenu avec la variante %s',
  (variante) => {
    render(<Texte variante={variante}>CH-2026-014</Texte>);

    expect(screen.getByText('CH-2026-014')).toBeVisible();
  },
);

it("n'a aucun défaut d'accessibilité détectable par axe", async () => {
  const { container } = render(
    <main>
      <Texte>Bienvenue sur le chantier</Texte>
    </main>,
  );

  await verifierAccessibilite(container);
});
