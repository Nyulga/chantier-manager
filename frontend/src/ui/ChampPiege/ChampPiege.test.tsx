// Tests du champ piège : invisible et inaccessible aux humains, mais présent et remplissable par un robot.
import { fireEvent, render, screen } from '@testing-library/react';
import { expect, it, vi } from 'vitest';

import { verifierAccessibilite } from '@/test/verifierAccessibilite';
import { ChampPiege } from './ChampPiege';

const surChangement = () => undefined;

function champDuDom(conteneur: HTMLElement) {
  const champ = conteneur.querySelector('input[name="site_web"]');
  if (!(champ instanceof HTMLInputElement)) {
    throw new Error('Le champ piège est absent du DOM.');
  }
  return champ;
}

it("n'est pas dans l'arbre d'accessibilité : ni par rôle, ni par libellé", () => {
  render(<ChampPiege valeur="" onChange={surChangement} />);

  expect(screen.queryByRole('textbox')).not.toBeInTheDocument();
  expect(screen.queryByLabelText(/site/i)).not.toBeInTheDocument();
});

it('reste dans le DOM, avec son nom : un robot qui remplit les champs le trouve', () => {
  const { container } = render(<ChampPiege valeur="" onChange={surChangement} />);

  const champ = champDuDom(container);
  expect(champ).toHaveAttribute('type', 'text');
  expect(champ).toHaveAttribute('name', 'site_web');
});

it('est masqué aux lecteurs d’écran, hors de la tabulation et sans saisie automatique', () => {
  const { container } = render(<ChampPiege valeur="" onChange={surChangement} />);

  const champ = champDuDom(container);
  expect(champ.closest('[aria-hidden="true"]')).not.toBeNull();
  expect(champ).toHaveAttribute('tabindex', '-1');
  expect(champ).toHaveAttribute('autocomplete', 'off');
});

it('remonte ce qu’un robot y écrit', () => {
  const onChange = vi.fn();
  const { container } = render(<ChampPiege valeur="" onChange={onChange} />);

  fireEvent.change(champDuDom(container), { target: { value: 'http://exemple.invalid' } });

  expect(onChange).toHaveBeenCalledWith('http://exemple.invalid');
});

it("n'a aucun défaut d'accessibilité détectable par axe", async () => {
  const { container } = render(<ChampPiege valeur="" onChange={surChangement} />);

  await verifierAccessibilite(container);
});
