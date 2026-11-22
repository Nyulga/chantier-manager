// Tests du composant `Champ` : libellé associé, types, saisie, erreur liée et accessibilité.
import { fireEvent, render, screen } from '@testing-library/react';
import { expect, it, vi } from 'vitest';

import { verifierAccessibilite } from '../test/verifierAccessibilite';
import { Champ } from './Champ';

const surChangement = () => undefined;

it('associe le libellé visible au champ de saisie', () => {
  render(<Champ libelle="Nom du chantier" valeur="" onChange={surChangement} />);

  expect(screen.getByLabelText('Nom du chantier')).toHaveAttribute('type', 'text');
});

it.each(['text', 'date', 'number'] as const)('accepte le type %s', (type) => {
  render(<Champ libelle="Valeur" type={type} valeur="" onChange={surChangement} />);

  expect(screen.getByLabelText('Valeur')).toHaveAttribute('type', type);
});

it('affiche la valeur reçue et remonte la saisie à onChange', () => {
  const onChange = vi.fn();
  render(<Champ libelle="Nom du chantier" valeur="Villa" onChange={onChange} />);

  const champ = screen.getByLabelText('Nom du chantier');
  fireEvent.change(champ, { target: { value: 'Villa Les Pins' } });

  expect(champ).toHaveValue('Villa');
  expect(onChange).toHaveBeenCalledWith('Villa Les Pins');
});

it('relie le message d’erreur au champ par aria-describedby', () => {
  render(
    <Champ
      libelle="Échéance"
      valeur=""
      onChange={surChangement}
      erreur="Indique une date, par exemple 31/12/2026."
    />,
  );

  const champ = screen.getByLabelText('Échéance');

  expect(champ).toHaveAccessibleDescription('Indique une date, par exemple 31/12/2026.');
  expect(champ).toBeInvalid();
});

it('n’a ni description ni état invalide quand il n’y a pas d’erreur', () => {
  render(<Champ libelle="Échéance" valeur="" onChange={surChangement} />);

  const champ = screen.getByLabelText('Échéance');

  expect(champ).not.toHaveAccessibleDescription();
  expect(champ).toBeValid();
});

it('signale un champ obligatoire', () => {
  render(<Champ libelle="Nom" valeur="" onChange={surChangement} requis />);

  expect(screen.getByLabelText('Nom')).toBeRequired();
});

it('n’a aucun défaut d’accessibilité détectable par axe, sans erreur', async () => {
  const { container } = render(<Champ libelle="Nom" valeur="" onChange={surChangement} />);

  await verifierAccessibilite(container);
});

it('n’a aucun défaut d’accessibilité détectable par axe, avec une erreur', async () => {
  const { container } = render(
    <Champ libelle="Nom" valeur="" onChange={surChangement} erreur="Ce champ est obligatoire." />,
  );

  await verifierAccessibilite(container);
});
