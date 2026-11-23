// Suite de tests commune aux deux hooks `useIdChantier` (chantiers et étapes) : ils ont le même contrat.
import { renderHook } from '@testing-library/react';
import type { ReactNode } from 'react';
import { MemoryRouter, Route, Routes } from 'react-router';
import { expect, it } from 'vitest';

/** Enveloppe qui monte la route de `chemin`, alors que l'adresse affichée est `/chantiers/abc`. */
function enveloppe(chemin: string) {
  return function Enveloppe({ children }: { readonly children: ReactNode }) {
    return (
      <MemoryRouter initialEntries={['/chantiers/abc']}>
        <Routes>
          <Route path={chemin} element={children} />
        </Routes>
      </MemoryRouter>
    );
  };
}

/**
 * Joue le contrat de `useIdChantier` : l'identifiant vient de l'adresse, et une route qui n'en a
 * pas est une erreur, jamais une valeur de remplacement qui enverrait une requête vide.
 */
export function testerUseIdChantier(useIdChantier: () => string) {
  it("renvoie l'identifiant du chantier de l'adresse", () => {
    const { result } = renderHook(() => useIdChantier(), { wrapper: enveloppe('chantiers/:id') });

    expect(result.current).toBe('abc');
  });

  it("refuse de servir une route qui n'a pas d'identifiant, plutôt que d'envoyer une requête vide", () => {
    expect(() =>
      renderHook(() => useIdChantier(), { wrapper: enveloppe('chantiers/:autre') }),
    ).toThrow(/identifiant/);
  });
}
