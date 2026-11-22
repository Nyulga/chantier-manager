// Fournisseurs globaux de l'application : requêtes serveur (TanStack Query) et routage.
// Aucun store global : l'état serveur vit dans TanStack Query, l'état local dans les composants.
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useState, type ReactNode } from 'react';
import { BrowserRouter } from 'react-router';

type ProvidersProps = {
  readonly children: ReactNode;
};

/**
 * Enveloppe l'application dans ses fournisseurs.
 *
 * Le client TanStack Query est créé une seule fois par montage (`useState`), et non au niveau
 * du module : chaque test, ou chaque rendu serveur futur, obtient ainsi un cache isolé.
 */
export function Providers({ children }: ProvidersProps) {
  const [clientRequetes] = useState(() => new QueryClient());

  return (
    <QueryClientProvider client={clientRequetes}>
      <BrowserRouter>{children}</BrowserRouter>
    </QueryClientProvider>
  );
}
