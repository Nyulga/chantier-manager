// Tests du hook `useProfilCourant` : lecture seule du profil choisi, mise à jour au changement.
import { act, renderHook } from '@testing-library/react';
import { afterEach, expect, it } from 'vitest';

import { enregistrerProfil } from '@/api/profil';

import { useProfilCourant } from './useProfilCourant';

afterEach(() => {
  localStorage.clear();
});

it('renvoie « chef » par défaut', () => {
  const { result } = renderHook(() => useProfilCourant());

  expect(result.current).toBe('chef');
});

it('suit le changement de profil', () => {
  const { result } = renderHook(() => useProfilCourant());

  act(() => {
    enregistrerProfil('ouvrier');
  });

  expect(result.current).toBe('ouvrier');
});
