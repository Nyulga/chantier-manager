// Aides de test des hooks de `services` : cache de requêtes neuf et enveloppe pour `renderHook`.
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import type { ReactNode } from 'react';

import { reessayerRequete } from '@/api/reessai';

/**
 * Crée un cache TanStack Query pour un test, avec la règle de nouvelle tentative de l'application
 * (`Providers`) : un refus de l'API (403, 404…) apparaît tout de suite, et une panne est rejouée,
 * mais sans attendre car le délai est nul. Chaque test a son propre cache : aucun résultat ne fuite
 * d'un test à l'autre.
 */
export function creerClientRequetes(): QueryClient {
  return new QueryClient({
    defaultOptions: { queries: { retry: reessayerRequete, retryDelay: 0 } },
  });
}

/** Enveloppe `renderHook` d'un cache de requêtes (celui que le test pourra espionner). */
export function creerEnveloppe(client: QueryClient) {
  return function Enveloppe({ children }: { readonly children: ReactNode }) {
    return <QueryClientProvider client={client}>{children}</QueryClientProvider>;
  };
}
