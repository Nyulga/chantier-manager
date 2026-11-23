// Tests de la `Section` : une région nommée par son titre de niveau 2, avec une action facultative.
import { render, screen } from '@testing-library/react';
import { createRef } from 'react';
import { expect, it } from 'vitest';

import { verifierAccessibilite } from '@/test/verifierAccessibilite';
import { Section } from './Section';

function afficher() {
  return render(
    <Section titre="Mes chantiers" action={<span>Voir tout</span>}>
      <p>Contenu</p>
    </Section>,
  );
}

it('est une région nommée par son titre, avec son contenu et son action', () => {
  afficher();

  expect(screen.getByRole('region', { name: 'Mes chantiers' })).toHaveTextContent('Contenu');
  expect(screen.getByRole('heading', { level: 2, name: 'Mes chantiers' })).toBeVisible();
  expect(screen.getByText('Voir tout')).toBeVisible();
});

it('rend son titre focalisable par programme quand une référence lui est donnée', () => {
  const reference = createRef<HTMLHeadingElement>();
  render(
    <Section titre="À valider" refTitre={reference}>
      <p>Rien à valider</p>
    </Section>,
  );

  reference.current?.focus();

  expect(screen.getByRole('heading', { level: 2, name: 'À valider' })).toHaveFocus();
});

it("n'a aucun défaut d'accessibilité détectable par axe", async () => {
  const { container } = afficher();

  await verifierAccessibilite(container);
});
