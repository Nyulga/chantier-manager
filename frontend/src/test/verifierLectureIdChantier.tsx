// Aide de test : la preuve commune des hooks `useIdChantier`, copiés dans chaque fonctionnalité.
import { renderHook } from '@testing-library/react';
import type { ReactNode } from 'react';
import { MemoryRouter, Route, Routes } from 'react-router';
import { expect, it, vi } from 'vitest';

/** Affiche `hook` sous une route `chemin`, visitée à l'adresse `adresse`. */
function afficherSousRoute(hook: () => string, chemin: string, adresse: string) {
  const Enveloppe = ({ children }: { readonly children: ReactNode }) => (
    <MemoryRouter initialEntries={[adresse]}>
      <Routes>
        <Route path={chemin} element={children} />
      </Routes>
    </MemoryRouter>
  );
  return renderHook(hook, { wrapper: Enveloppe });
}

/**
 * Déclare les deux tests d'un `useIdChantier`. Les fonctionnalités ne pouvant pas s'importer
 * l'une l'autre, chacune garde sa copie du hook, mais le branchement sur `useParams` se prouve
 * ici une seule fois pour toutes les copies.
 */
export function verifierLectureIdChantier(useIdChantier: () => string): void {
  it("renvoie l'identifiant du chantier lu dans l'adresse", () => {
    const { result } = afficherSousRoute(useIdChantier, '/chantiers/:id', '/chantiers/abc-123');

    expect(result.current).toBe('abc-123');
  });

  it("signale l'erreur quand la route n'a pas d'identifiant de chantier", () => {
    // React journalise l'erreur levée pendant le rendu : on la tait pour garder la sortie lisible.
    vi.spyOn(console, 'error').mockImplementation(() => undefined);

    expect(() => afficherSousRoute(useIdChantier, '/chantiers', '/chantiers')).toThrow(
      /identifiant de chantier/,
    );
  });
}
