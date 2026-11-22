// Tests des éléments de navigation : lien actif, compteur, et élément « Bientôt » désactivé.
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router';
import { expect, it } from 'vitest';

import { verifierAccessibilite } from '../test/verifierAccessibilite';
import { ElementNavigation } from './ElementNavigation';
import { ElementNavigationBientot } from './ElementNavigationBientot';

function afficher(adresse: string) {
  return render(
    <MemoryRouter initialEntries={[adresse]}>
      <ul>
        <ElementNavigation vers="/" exact icone="tableau-de-bord">
          Tableau de bord
        </ElementNavigation>
        <ElementNavigation vers="/chantiers" icone="chantiers" compteur={4}>
          Mes chantiers
        </ElementNavigation>
        <ElementNavigationBientot icone="equipe">Équipe</ElementNavigationBientot>
      </ul>
    </MemoryRouter>,
  );
}

it('marque la page courante avec aria-current="page"', () => {
  afficher('/');

  expect(screen.getByRole('link', { name: 'Tableau de bord' })).toHaveAttribute(
    'aria-current',
    'page',
  );
  expect(screen.getByRole('link', { name: /Mes chantiers/ })).not.toHaveAttribute('aria-current');
});

it('reste actif sur les pages enfants quand la correspondance n’est pas exacte', () => {
  afficher('/chantiers/42');

  expect(screen.getByRole('link', { name: /Mes chantiers/ })).toHaveAttribute(
    'aria-current',
    'page',
  );
  expect(screen.getByRole('link', { name: 'Tableau de bord' })).not.toHaveAttribute('aria-current');
});

it('affiche le compteur dans le nom du lien', () => {
  afficher('/');

  expect(screen.getByRole('link', { name: 'Mes chantiers 4' })).toHaveAttribute(
    'href',
    '/chantiers',
  );
});

it('affiche l’élément « Bientôt » sans lien, avec sa mention visible', () => {
  afficher('/');

  expect(screen.queryByRole('link', { name: /Équipe/ })).not.toBeInTheDocument();
  expect(screen.getByText('Équipe')).toBeVisible();
  expect(screen.getByText('Bientôt')).toBeVisible();
});

it('n’a aucun défaut d’accessibilité détectable par axe', async () => {
  const { container } = afficher('/');

  await verifierAccessibilite(container);
});
