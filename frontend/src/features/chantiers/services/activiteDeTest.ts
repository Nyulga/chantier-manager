// Entrée d'activité d'exemple pour les tests des services et des pages du tableau de bord.
import type { EntreeActivite } from './useActiviteRecente';

/** Une entrée du fil d'activité, telle que l'API la renvoie ; `surcharges` change les champs voulus. */
export function activiteDeTest(surcharges: Partial<EntreeActivite> = {}): EntreeActivite {
  return {
    etape_id: '0198f1a0-0000-7000-8000-0000000000e1',
    chantier_id: '0198f1a0-0000-7000-8000-000000000001',
    titre_etape: 'Pose des meubles',
    role: 'ouvrier',
    ancien_statut: 'en_cours',
    nouveau_statut: 'terminee_a_valider',
    date: '2026-11-21T17:42:00+01:00',
    commentaire: null,
    ...surcharges,
  };
}
