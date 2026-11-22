// Tests du composant `BadgeStatut` : le statut s'écrit toujours en toutes lettres, en français.
import { render, screen } from '@testing-library/react';
import { expect, it } from 'vitest';

import { verifierAccessibilite } from '../test/verifierAccessibilite';
import { BadgeStatut, type StatutEtape } from './BadgeStatut';

const LIBELLES: readonly (readonly [StatutEtape, string])[] = [
  ['a_faire', 'À faire'],
  ['en_cours', 'En cours'],
  ['terminee_a_valider', 'Terminée (à valider)'],
  ['validee', 'Validée'],
];

it.each(LIBELLES)('affiche le statut %s en toutes lettres : « %s »', (statut, libelle) => {
  render(<BadgeStatut statut={statut} />);

  expect(screen.getByText(libelle)).toBeVisible();
});

it.each(LIBELLES)(
  'le statut %s n’a aucun défaut d’accessibilité détectable par axe',
  async (statut) => {
    const { container } = render(<BadgeStatut statut={statut} />);

    await verifierAccessibilite(container);
  },
);
