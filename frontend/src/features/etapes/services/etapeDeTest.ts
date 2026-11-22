// Étape d'exemple pour les tests des services et des pages de la fonctionnalité.
import type { Etape } from './useEtapes';

/** Une étape valide, telle que l'API la renvoie ; `surcharges` change les champs voulus. */
export function etapeDeTest(surcharges: Partial<Etape> = {}): Etape {
  return {
    id: '0198f1a0-0000-7000-8000-0000000000e1',
    chantier_id: '0198f1a0-0000-7000-8000-000000000001',
    titre: 'Fondations',
    ordre: 1,
    statut: 'a_faire',
    version: 1,
    actions_permises: ['demarrer'],
    ...surcharges,
  };
}
