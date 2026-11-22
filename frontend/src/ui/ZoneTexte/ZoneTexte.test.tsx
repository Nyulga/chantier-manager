// Tests du composant `ZoneTexte` : libellé associé, saisie, erreur liée et accessibilité.
import { fireEvent, render, screen } from '@testing-library/react';
import { expect, it, vi } from 'vitest';

import { verifierAccessibilite } from '../test/verifierAccessibilite';
import { ZoneTexte } from './ZoneTexte';

const surChangement = () => undefined;

it('associe le libellé visible à la zone de saisie', () => {
  render(<ZoneTexte libelle="Motif du refus" valeur="" onChange={surChangement} />);

  expect(screen.getByRole('textbox', { name: 'Motif du refus' })).toBeVisible();
});

it('affiche la valeur reçue et remonte la saisie à onChange', () => {
  const onChange = vi.fn();
  render(<ZoneTexte libelle="Motif du refus" valeur="Trop court" onChange={onChange} />);

  const zone = screen.getByRole('textbox', { name: 'Motif du refus' });
  fireEvent.change(zone, { target: { value: 'Les joints sont à refaire.' } });

  expect(zone).toHaveValue('Trop court');
  expect(onChange).toHaveBeenCalledWith('Les joints sont à refaire.');
});

it('relie le message d’erreur à la zone par aria-describedby', () => {
  render(
    <ZoneTexte
      libelle="Motif du refus"
      valeur=""
      onChange={surChangement}
      erreur="Explique ce qui doit être corrigé."
    />,
  );

  const zone = screen.getByRole('textbox', { name: 'Motif du refus' });

  expect(zone).toHaveAccessibleDescription('Explique ce qui doit être corrigé.');
  expect(zone).toBeInvalid();
});

it('n’a aucun défaut d’accessibilité détectable par axe, sans erreur', async () => {
  const { container } = render(<ZoneTexte libelle="Motif" valeur="" onChange={surChangement} />);

  await verifierAccessibilite(container);
});

it('n’a aucun défaut d’accessibilité détectable par axe, avec une erreur', async () => {
  const { container } = render(
    <ZoneTexte
      libelle="Motif"
      valeur=""
      onChange={surChangement}
      erreur="Le motif est obligatoire."
    />,
  );

  await verifierAccessibilite(container);
});
