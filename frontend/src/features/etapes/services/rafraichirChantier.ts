// Rafraîchissement du cache après une modification des étapes d'un chantier.
import type { QueryClient } from '@tanstack/react-query';

import { clesRequetes } from '@/api/clesRequetes';

/**
 * Invalide ce qu'une modification d'étape peut avoir changé : la liste des chantiers et le
 * chantier concerné (leur avancement est calculé par l'API), et la liste de ses étapes.
 */
export async function rafraichirChantier(
  clientRequetes: QueryClient,
  chantierId: string,
): Promise<void> {
  await Promise.all([
    clientRequetes.invalidateQueries({ queryKey: clesRequetes.listeChantiers() }),
    clientRequetes.invalidateQueries({ queryKey: clesRequetes.chantier(chantierId) }),
    clientRequetes.invalidateQueries({ queryKey: clesRequetes.etapes(chantierId) }),
  ]);
}
