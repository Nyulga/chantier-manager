// Hook de la liste des chantiers : ce que l'acteur courant a le droit de voir, selon l'API.
import { useQuery } from '@tanstack/react-query';

import { listerChantiers } from '@/api/chantiers';
import { clesRequetes } from '@/api/clesRequetes';
import type { components } from '@/api/schema';

/** Chantier tel que l'API le renvoie : budget `null` pour un ouvrier, avancement déjà calculé. */
export type Chantier = components['schemas']['ChantierReponse'];

/** Liste les chantiers. Le périmètre et la visibilité du budget sont décidés par l'API. */
export function useChantiers() {
  return useQuery({
    queryKey: clesRequetes.listeChantiers(),
    queryFn: listerChantiers,
  });
}
