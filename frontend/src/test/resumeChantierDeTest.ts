// Résumé de chantier d'exemple, tel que les hooks de liste le donnent aux composants (déjà prêt pour la carte).
import type { ChantierDeListe } from '@/api/chantiers';

/** Un chantier de la liste ; `surcharges` change les champs voulus. */
export function resumeChantierDeTest(surcharges: Partial<ChantierDeListe> = {}): ChantierDeListe {
  return {
    id: '0198f1a0-0000-7000-8000-000000000001',
    nom: 'Rénovation de la mairie',
    adresse: '12 rue des Lilas, 69003 Lyon',
    etapesValidees: 3,
    etapesTotal: 6,
    avancement: 50,
    etapesAValider: 0,
    echeance: '2026-09-30',
    joursRestants: 54,
    enRetard: false,
    ...surcharges,
  };
}
