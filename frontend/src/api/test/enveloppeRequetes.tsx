// Aides de test des hooks de `services` : cache de requêtes neuf et enveloppe pour `renderHook`.
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import type { ReactNode } from 'react';

/**
 * Crée un cache TanStack Query pour un test, sans nouvelle tentative : une erreur de l'API
 * apparaît tout de suite, et aucun résultat ne fuite d'un test à l'autre.
 */
export function creerClientRequetes(): QueryClient {
  return new QueryClient({ defaultOptions: { queries: { retry: false } } });
}

/** Enveloppe `renderHook` d'un cache de requêtes (celui que le test pourra espionner). */
export function creerEnveloppe(client: QueryClient) {
  return function Enveloppe({ children }: { readonly children: ReactNode }) {
    return <QueryClientProvider client={client}>{children}</QueryClientProvider>;
  };
}
