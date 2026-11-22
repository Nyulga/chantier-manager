// Tests de `ElementNavigationBientot` : une entrée de navigation désactivée, qui dit pourquoi.
import { render, screen } from '@testing-library/react';
import { expect, it } from 'vitest';

import { verifierAccessibilite } from '../test/verifierAccessibilite';
import { ElementNavigationBientot } from './ElementNavigationBientot';

function afficher() {
  return render(
    <ul>
      <ElementNavigationBientot icone="equipe">Équipe</ElementNavigationBientot>
    </ul>,
  );
}

it('affiche le libellé et la mention « Bientôt », en toutes lettres', () => {
  afficher();

  expect(screen.getByText('Équipe')).toBeVisible();
  expect(screen.getByText('Bientôt')).toBeVisible();
});

it('n’est pas un lien : le clavier ne s’y arrête pas, et l’état désactivé est annoncé', () => {
  afficher();

  expect(screen.queryByRole('link')).not.toBeInTheDocument();
  expect(screen.getByText('Équipe').closest('[aria-disabled="true"]')).toBeInTheDocument();
});

it('n’a aucun défaut d’accessibilité détectable par axe', async () => {
  const { container } = afficher();

  await verifierAccessibilite(container);
});
