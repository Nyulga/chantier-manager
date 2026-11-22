// Tests du composant `FilActivite` : une liste ordonnée d'événements, du plus récent au plus ancien.
import { render, screen, within } from '@testing-library/react';
import { expect, it } from 'vitest';

import { verifierAccessibilite } from '../test/verifierAccessibilite';
import { FilActivite } from './FilActivite';

const ENTREES = [
  {
    id: 'a',
    initiales: 'TU',
    qui: 'Tu',
    quoi: 'as validé « Fondations »',
    contexte: 'Mairie · hier',
  },
  {
    id: 'b',
    initiales: 'OU',
    qui: 'L’ouvrier',
    quoi: 'a démarré « Gros œuvre »',
    contexte: 'Mairie · lundi',
  },
];

it('affiche une ligne par événement : qui, quoi, puis le contexte', () => {
  render(<FilActivite libelle="Activité récente" entrees={ENTREES} />);

  const liste = screen.getByRole('list', { name: 'Activité récente' });
  const lignes = within(liste).getAllByRole('listitem');
  expect(lignes).toHaveLength(2);
  expect(lignes[0]).toHaveTextContent('Tu as validé « Fondations »');
  expect(lignes[0]).toHaveTextContent('Mairie · hier');
});

it('n’a aucun défaut d’accessibilité détectable par axe', async () => {
  const { container } = render(<FilActivite libelle="Activité récente" entrees={ENTREES} />);

  await verifierAccessibilite(container);
});
