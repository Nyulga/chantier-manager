// Étape à valider d'exemple pour les tests des services et des pages du tableau de bord.
import type { EtapeAValider } from './useEtapesAValider';

/** Une étape signalée terminée, telle que l'API la renvoie au chef ; `surcharges` change les champs voulus. */
export function etapeAValiderDeTest(surcharges: Partial<EtapeAValider> = {}): EtapeAValider {
  return {
    id: '0198f1a0-0000-7000-8000-0000000000e1',
    chantier_id: '0198f1a0-0000-7000-8000-000000000001',
    titre: 'Pose des meubles',
    version: 3,
    actions_permises: ['valider', 'refuser'],
    signalee_le: '2026-11-21T17:42:00+01:00',
    ...surcharges,
  };
}
