// Tests du composant `Alerte` : une erreur est annoncée tout de suite, une information discrètement.
import { render, screen } from '@testing-library/react';
import { expect, it } from 'vitest';

import { verifierAccessibilite } from '../test/verifierAccessibilite';
import { Alerte } from './Alerte';

it('annonce une erreur avec role="alert" et la nomme en toutes lettres', () => {
  render(<Alerte variante="erreur">Le serveur ne répond pas.</Alerte>);

  const alerte = screen.getByRole('alert');

  expect(alerte).toHaveTextContent('Erreur');
  expect(alerte).toHaveTextContent('Le serveur ne répond pas.');
});

it('affiche une information sans l’annoncer comme une alerte', () => {
  render(<Alerte variante="information">C’est envoyé.</Alerte>);

  expect(screen.queryByRole('alert')).not.toBeInTheDocument();
  expect(screen.getByRole('status')).toHaveTextContent('Information');
  expect(screen.getByRole('status')).toHaveTextContent('C’est envoyé.');
});

it.each(['erreur', 'information'] as const)(
  'la variante %s n’a aucun défaut d’accessibilité détectable par axe',
  async (variante) => {
    const { container } = render(<Alerte variante={variante}>Message</Alerte>);

    await verifierAccessibilite(container);
  },
);
