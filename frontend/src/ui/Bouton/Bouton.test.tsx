// Tests du composant `Bouton` : variantes, type, état désactivé, clic et accessibilité.
import { fireEvent, render, screen } from '@testing-library/react';
import { expect, it, vi } from 'vitest';

import { verifierAccessibilite } from '../test/verifierAccessibilite';
import { Bouton } from './Bouton';

it('affiche un bouton nommé par son libellé, de type « button » par défaut', () => {
  render(<Bouton>Valider l’étape</Bouton>);

  // Un bouton sans type explicite enverrait le formulaire qui le contient : on l'évite.
  expect(screen.getByRole('button', { name: 'Valider l’étape' })).toHaveAttribute('type', 'button');
});

it('peut être un bouton d’envoi de formulaire', () => {
  render(<Bouton type="submit">Envoyer le refus</Bouton>);

  expect(screen.getByRole('button', { name: 'Envoyer le refus' })).toHaveAttribute(
    'type',
    'submit',
  );
});

it('appelle onClick au clic', () => {
  const onClick = vi.fn();
  render(<Bouton onClick={onClick}>Signaler terminée</Bouton>);

  fireEvent.click(screen.getByRole('button', { name: 'Signaler terminée' }));

  expect(onClick).toHaveBeenCalledOnce();
});

it('ne réagit pas au clic quand il est désactivé', () => {
  const onClick = vi.fn();
  render(
    <Bouton disabled onClick={onClick}>
      Valider l’étape
    </Bouton>,
  );

  const bouton = screen.getByRole('button', { name: 'Valider l’étape' });
  fireEvent.click(bouton);

  expect(bouton).toBeDisabled();
  expect(onClick).not.toHaveBeenCalled();
});

it.each(['principal', 'secondaire', 'danger'] as const)(
  'la variante %s n’a aucun défaut d’accessibilité détectable par axe',
  async (variante) => {
    const { container } = render(<Bouton variante={variante}>Action</Bouton>);

    await verifierAccessibilite(container);
  },
);
