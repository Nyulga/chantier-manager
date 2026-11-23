// Tests de la `LigneAValider` : une étape signalée terminée, avec son contexte et ses actions.
import { render, screen } from '@testing-library/react';
import { createRef } from 'react';
import { expect, it } from 'vitest';

import { verifierAccessibilite } from '@/test/verifierAccessibilite';
import { LigneAValider } from './LigneAValider';

function afficher(reference = createRef<HTMLLIElement>()) {
  return render(
    <ul>
      <LigneAValider
        ref={reference}
        titre="Pose des meubles"
        contexte="Rénovation cuisine"
        signalement="Signalée hier à 17:42"
        actions={<button type="button">Valider</button>}
      />
    </ul>,
  );
}

it("affiche le titre, le chantier, le signalement et les actions de l'étape", () => {
  afficher();

  const ligne = screen.getByRole('listitem');
  expect(ligne).toHaveTextContent('Pose des meubles');
  expect(ligne).toHaveTextContent('Rénovation cuisine');
  expect(ligne).toHaveTextContent('Signalée hier à 17:42');
  expect(ligne).toContainElement(screen.getByRole('button', { name: 'Valider' }));
});

it("peut recevoir le focus par programme sans entrer dans l'ordre de tabulation", () => {
  const reference = createRef<HTMLLIElement>();
  afficher(reference);

  reference.current?.focus();

  expect(screen.getByRole('listitem')).toHaveFocus();
  expect(screen.getByRole('listitem')).toHaveAttribute('tabindex', '-1');
});

it("n'a aucun défaut d'accessibilité détectable par axe", async () => {
  const { container } = afficher();

  await verifierAccessibilite(container);
});
