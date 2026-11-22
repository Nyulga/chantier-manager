// Aides de test : cache de requêtes neuf et affichage de routes.
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { render } from '@testing-library/react';
import type { ReactElement } from 'react';
import { MemoryRouter } from 'react-router';

/**
 * Crée un cache TanStack Query pour un test, sans nouvelle tentative par défaut (et sans délai quand un hook impose les siennes) : une erreur de l'API
 * apparaît tout de suite, et aucun résultat ne fuite d'un test à l'autre.
 */
export function creerClientRequetes(): QueryClient {
  return new QueryClient({ defaultOptions: { queries: { retry: false, retryDelay: 0 } } });
}

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
