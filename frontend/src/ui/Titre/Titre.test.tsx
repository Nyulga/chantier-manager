// Tests du composant `Titre` : le niveau choisi détermine l'élément de titre HTML.
import { render, screen } from '@testing-library/react';

import { expect, it } from 'vitest';

import { verifierAccessibilite } from '../test/verifierAccessibilite';
import { Titre } from './Titre';

it.each([1, 2, 3] as const)(
  'rend un titre HTML de niveau %i quand on demande ce niveau',
  (niveau) => {
    render(<Titre niveau={niveau}>Chantier Manager</Titre>);

    expect(screen.getByRole('heading', { level: niveau, name: 'Chantier Manager' })).toBeVisible();
  },
);

it("n'a aucun défaut d'accessibilité détectable par axe", async () => {
  const { container } = render(
    <main>
      <Titre niveau={1}>Chantier Manager</Titre>
    </main>,
  );

  await verifierAccessibilite(container);
});
