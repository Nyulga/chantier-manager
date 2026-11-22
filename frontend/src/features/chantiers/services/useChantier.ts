// Hook d'un chantier : ses informations et son avancement, tels que l'API les renvoie.
import { useQuery } from '@tanstack/react-query';

import { creerClientApi } from '@/api/client';
import { clesRequetes } from '@/api/clesRequetes';
import { erreurApi } from '@/api/erreurApi';

/** Consulte un chantier. Un chantier inconnu ou hors périmètre donne une erreur 404 de l'API. */
export function useChantier(id: string) {
  return useQuery({
    queryKey: clesRequetes.chantier(id),
    queryFn: async () => {
      const { data, error } = await creerClientApi().GET('/chantiers/{chantier_id}', {
        params: { path: { chantier_id: id } },
      });
      if (data === undefined) {
        throw erreurApi(error);
      }
      return data;
    },
  });
}
