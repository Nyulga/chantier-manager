// Hook d'un chantier : ses informations et son avancement, tels que l'API les renvoie.
import { useQuery } from '@tanstack/react-query';

import { clesRequetes } from '@/api/clesRequetes';
import { lireChantier } from '@/api/chantiers';

/** Chantier tel que l'API le renvoie : budget `null` pour un ouvrier, avancement déjà calculé. */
export type { Chantier } from '@/api/chantiers';

/** Consulte un chantier. Un chantier inconnu donne une erreur 404 de l'API (`error.introuvable`). */
export function useChantier(id: string) {
  return useQuery({
    queryKey: clesRequetes.chantier(id),
    queryFn: () => lireChantier(id),
  });
}
