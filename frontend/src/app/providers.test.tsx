// Tests des fournisseurs globaux : ils affichent leurs enfants et fournissent TanStack Query.
import { useQueryClient } from '@tanstack/react-query';
import { render, screen } from '@testing-library/react';
import { expect, it } from 'vitest';

import { Providers } from './providers';

/** Composant de test : n'affiche du texte que si un client TanStack Query est disponible. */
function SondeClientRequetes() {
  useQueryClient();
  return <p>Client de requêtes disponible</p>;
}

it('fournit le client TanStack Query aux composants enfants', () => {
  render(
    <Providers>
      <SondeClientRequetes />
    </Providers>,
  );

  expect(screen.getByText('Client de requêtes disponible')).toBeVisible();
});
