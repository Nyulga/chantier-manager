// Aide de test : affiche des routes dans un cache de requêtes neuf.
import { QueryClientProvider } from '@tanstack/react-query';
import { render } from '@testing-library/react';
import type { ReactElement } from 'react';
import { MemoryRouter } from 'react-router';

import { creerClientRequetes } from './enveloppeRequetes';

/**
 * Affiche `routes` à l'adresse `adresse`, comme le font `Providers` et `BrowserRouter` en
 * production. Le cache est renvoyé pour pouvoir observer les invalidations.
 */
export function afficherAvecFournisseurs(routes: ReactElement, adresse = '/') {
  const client = creerClientRequetes();
  const rendu = render(
    <QueryClientProvider client={client}>
      <MemoryRouter initialEntries={[adresse]}>{routes}</MemoryRouter>
    </QueryClientProvider>,
  );

  return { ...rendu, client };
}
