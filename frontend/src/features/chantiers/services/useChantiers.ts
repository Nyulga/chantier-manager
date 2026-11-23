// Hook de la liste des chantiers : ce que l'acteur courant a le droit de voir, selon l'API.
import { useQuery } from '@tanstack/react-query';

import { optionsListeChantiers } from '@/api/chantiers';
import type { components } from '@/api/schema';

/** Chantier tel que l'API le renvoie : budget `null` pour un ouvrier, avancement déjà calculé. */
export type Chantier = components['schemas']['ChantierReponse'];

/** Liste les chantiers que l'API renvoie ; elle décide aussi de la visibilité du budget. */
export function useChantiers() {
  return useQuery(optionsListeChantiers);
}
