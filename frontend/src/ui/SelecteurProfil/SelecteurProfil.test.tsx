// Tests du composant `SelecteurProfil` : choix Chef ou Ouvrier, contrôlé par ses props.
import { fireEvent, render, screen } from '@testing-library/react';
import { expect, it, vi } from 'vitest';

import { verifierAccessibilite } from '../test/verifierAccessibilite';
import { SelecteurProfil } from './SelecteurProfil';

it('propose Chef et Ouvrier dans un groupe nommé « Profil »', () => {
  render(<SelecteurProfil valeur="chef" onChange={vi.fn()} />);

  expect(screen.getByRole('radiogroup', { name: 'Profil' })).toBeVisible();
  expect(screen.getByRole('radio', { name: 'Chef' })).toBeChecked();
  expect(screen.getByRole('radio', { name: 'Ouvrier' })).not.toBeChecked();
});

it('coche le profil reçu dans ses props', () => {
  render(<SelecteurProfil valeur="ouvrier" onChange={vi.fn()} />);

  expect(screen.getByRole('radio', { name: 'Ouvrier' })).toBeChecked();
});

it('remonte le profil choisi à onChange', () => {
  const onChange = vi.fn();
  render(<SelecteurProfil valeur="chef" onChange={onChange} />);

  fireEvent.click(screen.getByRole('radio', { name: 'Ouvrier' }));

  expect(onChange).toHaveBeenCalledWith('ouvrier');
});

it('n’a aucun défaut d’accessibilité détectable par axe', async () => {
  const { container } = render(<SelecteurProfil valeur="chef" onChange={vi.fn()} />);

  await verifierAccessibilite(container);
});
