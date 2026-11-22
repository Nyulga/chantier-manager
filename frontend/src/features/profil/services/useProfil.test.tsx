// Tests du hook `useProfil` : lecture, changement et rafraîchissement des données du profil.
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { act, renderHook } from '@testing-library/react';
import type { ReactNode } from 'react';
import { afterEach, expect, it, vi } from 'vitest';

import { useProfil } from './useProfil';

afterEach(() => {
  localStorage.clear();
});

function creerEnveloppe(client: QueryClient) {
  return function Enveloppe({ children }: { readonly children: ReactNode }) {
    return <QueryClientProvider client={client}>{children}</QueryClientProvider>;
  };
}

it('renvoie « chef » par défaut', () => {
  const { result } = renderHook(() => useProfil(), { wrapper: creerEnveloppe(new QueryClient()) });

  expect(result.current.profil).toBe('chef');
});

it('lit le profil déjà enregistré', () => {
  localStorage.setItem('chantier-manager.profil', 'ouvrier');

  const { result } = renderHook(() => useProfil(), { wrapper: creerEnveloppe(new QueryClient()) });

  expect(result.current.profil).toBe('ouvrier');
});

it('change le profil, le sauvegarde et met à jour les composants', () => {
  const { result } = renderHook(() => useProfil(), { wrapper: creerEnveloppe(new QueryClient()) });

  act(() => {
    result.current.changerProfil('ouvrier');
  });

  expect(result.current.profil).toBe('ouvrier');
  expect(localStorage.getItem('chantier-manager.profil')).toBe('ouvrier');
});

it('invalide les requêtes en cache : leurs données dépendaient de l’ancien profil', () => {
  const client = new QueryClient();
  const invalider = vi.spyOn(client, 'invalidateQueries');
  const { result } = renderHook(() => useProfil(), { wrapper: creerEnveloppe(client) });

  act(() => {
    result.current.changerProfil('ouvrier');
  });

  expect(invalider).toHaveBeenCalledOnce();
});
