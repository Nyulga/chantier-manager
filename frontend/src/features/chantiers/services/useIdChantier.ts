// Hook de l'identifiant du chantier affiché, lu dans l'adresse de la page (`/chantiers/:id`).
import { useParams } from 'react-router';

import { lireIdentifiantChantier } from '@/api/identifiantChantier';

/** Renvoie l'identifiant du chantier de l'adresse ; la validation est partagée avec les autres fonctionnalités. */
export function useIdChantier(): string {
  const { id } = useParams();
  return lireIdentifiantChantier(id);
}
