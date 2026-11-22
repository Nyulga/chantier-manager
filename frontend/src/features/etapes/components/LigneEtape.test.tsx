// Tests de la ligne d'étape : le formulaire de refus suit les actions permises par l'API.
import { fireEvent, render, screen } from '@testing-library/react';
import { expect, it, vi } from 'vitest';

import type { Etape } from '../services/useEtapes';
import { LigneEtape } from './LigneEtape';

const ETAPE: Etape = {
  id: 'e1',
  chantier_id: 'c1',
  titre: 'Fondations',
  ordre: 1,
  statut: 'terminee_a_valider',
  version: 1,
  actions_permises: ['valider', 'refuser'],
};

it('ferme le formulaire de refus quand l’API ne permet plus de refuser', () => {
  const { rerender } = render(<LigneEtape etape={ETAPE} enCours={false} onAction={vi.fn()} />);
  fireEvent.click(screen.getByRole('button', { name: 'Refuser : Fondations' }));
  expect(screen.getByLabelText('Motif du refus')).toBeVisible();

  rerender(
    <LigneEtape
      etape={{ ...ETAPE, statut: 'validee', actions_permises: [] }}
      enCours={false}
      onAction={vi.fn()}
    />,
  );

  expect(screen.queryByLabelText('Motif du refus')).not.toBeInTheDocument();
});

it('affiche l’erreur sous le champ du motif quand le refus est ouvert', () => {
  render(
    <LigneEtape
      etape={ETAPE}
      enCours={false}
      erreur="Le commentaire du refus est obligatoire."
      onAction={vi.fn()}
    />,
  );
  expect(screen.getByRole('alert')).toBeVisible();

  fireEvent.click(screen.getByRole('button', { name: 'Refuser : Fondations' }));

  expect(screen.getByLabelText('Motif du refus')).toHaveAccessibleDescription(
    'Le commentaire du refus est obligatoire.',
  );
  expect(screen.queryByRole('alert')).not.toBeInTheDocument();
});
