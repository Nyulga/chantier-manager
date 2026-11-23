// Hook de la liste des chantiers : ce que l'acteur courant a le droit de voir, selon l'API.
import { useQuery } from '@tanstack/react-query';

import { optionsListeChantiers } from '@/api/chantiers';

/** Chantier de la liste, réduit à ce que sa carte affiche (le budget n'en fait pas partie). */
export type { ChantierDeListe } from '@/api/chantiers';

/** Liste les chantiers que l'API renvoie ; elle décide aussi du périmètre de l'acteur. */
export function useChantiers() {
  return useQuery(optionsListeChantiers);
}
