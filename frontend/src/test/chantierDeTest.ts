// Chantier d'exemple pour les tests des services, des composants et des pages.
import type { components } from '@/api/schema';

type Chantier = components['schemas']['ChantierReponse'];

/** Un chantier valide, tel que l'API le renvoie à un chef ; `surcharges` change les champs voulus. */
export function chantierDeTest(surcharges: Partial<Chantier> = {}): Chantier {
  return {
    id: '0198f1a0-0000-7000-8000-000000000001',
    nom: 'Rénovation de la mairie',
    adresse: { voie: '12 rue des Lilas', code_postal: '69003', ville: 'Lyon' },
    client: 'Mairie de Lyon',
    date_debut: '2026-03-02',
    echeance: '2026-09-30',
    budget: '18450.00',
    avancement: 50,
    peut_ajouter_etape: true,
    etapes_validees: 3,
    etapes_total: 6,
    etapes_a_valider: 0,
    jours_restants: 54,
    en_retard: false,
    ...surcharges,
  };
}
