// Tests de la ligne d'étape : le formulaire de refus suit les actions permises par l'API.
import { fireEvent, render, screen } from '@testing-library/react';
import { expect, it, vi } from 'vitest';

import { erreurApiDeTest } from '@/test/erreurApiDeTest';
import { etapeDeTest } from '@/test/etapeDeTest';

import { LigneEtape } from './LigneEtape';

const ETAPE = etapeDeTest({
  titre: 'Fondations',
  statut: 'terminee_a_valider',
  actions_permises: ['valider', 'refuser'],
});
const ETAPE_VALIDEE = etapeDeTest({ titre: 'Fondations', statut: 'validee', actions_permises: [] });

it("ferme le formulaire de refus quand l'API ne permet plus de refuser", () => {
  const { rerender } = render(<LigneEtape etape={ETAPE} enCours={false} onAction={vi.fn()} />);
  fireEvent.click(screen.getByRole('button', { name: 'Refuser : Fondations' }));
  expect(screen.getByLabelText('Motif du refus')).toBeVisible();

  rerender(<LigneEtape etape={ETAPE_VALIDEE} enCours={false} onAction={vi.fn()} />);

  expect(screen.queryByLabelText('Motif du refus')).not.toBeInTheDocument();
});

it("ne rouvre pas tout seul le formulaire quand l'API permet de nouveau de refuser", () => {
  const { rerender } = render(<LigneEtape etape={ETAPE} enCours={false} onAction={vi.fn()} />);
  fireEvent.click(screen.getByRole('button', { name: 'Refuser : Fondations' }));
  rerender(<LigneEtape etape={ETAPE_VALIDEE} enCours={false} onAction={vi.fn()} />);

  rerender(<LigneEtape etape={ETAPE} enCours={false} onAction={vi.fn()} />);

  expect(screen.getByRole('button', { name: 'Refuser : Fondations' })).toBeVisible();
  expect(screen.queryByLabelText('Motif du refus')).not.toBeInTheDocument();
});

it("annonce l'erreur du motif sous le champ, dès l'ouverture du refus", () => {
  const erreur = erreurApiDeTest('Les données envoyées sont invalides.', [
    { champ: 'commentaire', message: 'Le commentaire du refus est obligatoire.' },
  ]);
  render(<LigneEtape etape={ETAPE} enCours={false} erreur={erreur} onAction={vi.fn()} />);

  fireEvent.click(screen.getByRole('button', { name: 'Refuser : Fondations' }));

  expect(screen.getByLabelText('Motif du refus')).toHaveAccessibleDescription(
    'Le commentaire du refus est obligatoire.',
  );
  expect(screen.getByRole('alert')).toHaveTextContent('Le commentaire du refus est obligatoire.');
});

it("montre l'erreur dans la carte quand le formulaire de refus n'est pas ouvert", () => {
  const erreur = erreurApiDeTest('Cette étape a déjà changé de statut.');

  render(<LigneEtape etape={ETAPE} enCours={false} erreur={erreur} onAction={vi.fn()} />);

  expect(screen.getByRole('alert')).toHaveTextContent('Cette étape a déjà changé de statut.');
});
