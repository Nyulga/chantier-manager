// Tests de l'`EntetePage` : surtitre, titre de niveau 1 et zone d'actions.
import { render, screen } from '@testing-library/react';
import { expect, it } from 'vitest';

import { verifierAccessibilite } from '@/test/verifierAccessibilite';
import { EntetePage } from './EntetePage';

function afficher() {
  return render(
    <EntetePage surtitre="dimanche 22 novembre 2026" titre="Tableau de bord">
      <button type="button">Action</button>
    </EntetePage>,
  );
}

it('affiche le surtitre, le titre de niveau 1 et les actions', () => {
  afficher();

  expect(screen.getByText('dimanche 22 novembre 2026')).toBeVisible();
  expect(screen.getByRole('heading', { level: 1, name: 'Tableau de bord' })).toBeVisible();
  expect(screen.getByRole('button', { name: 'Action' })).toBeVisible();
});

it('affiche un titre seul, sans surtitre ni actions', () => {
  render(<EntetePage titre="Chantiers" />);

  expect(screen.getByRole('heading', { level: 1, name: 'Chantiers' })).toBeVisible();
});

it("n'a aucun défaut d'accessibilité détectable par axe", async () => {
  const { container } = afficher();

  await verifierAccessibilite(container);
});
