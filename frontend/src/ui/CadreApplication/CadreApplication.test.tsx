// Tests du `CadreApplication` : la barre latérale et la zone principale unique de l'écran.
import { render, screen } from '@testing-library/react';
import { expect, it } from 'vitest';

import { verifierAccessibilite } from '@/test/verifierAccessibilite';
import { CadreApplication } from './CadreApplication';

function afficher() {
  return render(
    <CadreApplication barreLaterale={<aside>Barre</aside>}>Contenu de la page</CadreApplication>,
  );
}

it('affiche la barre latérale puis le contenu dans la zone principale', () => {
  afficher();

  expect(screen.getByText('Barre')).toBeVisible();
  expect(screen.getByRole('main')).toHaveTextContent('Contenu de la page');
});

it("n'a aucun défaut d'accessibilité détectable par axe", async () => {
  const { container } = afficher();

  await verifierAccessibilite(container);
});
