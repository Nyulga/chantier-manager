// Hook du fil d'activité : les derniers changements de statut d'étapes, du plus récent au plus ancien.
import { useQuery } from '@tanstack/react-query';

import { clesRequetes } from '@/api/clesRequetes';
import { creerClientApi } from '@/api/client';
import { erreurApi } from '@/api/erreurApi';
import type { components } from '@/api/schema';

/** Une entrée du fil : qui (le rôle) a fait passer quelle étape de quel statut à quel statut. */
export type EntreeActivite = components['schemas']['ActiviteReponse'];

/** Nombre d'entrées demandées par défaut : de quoi remplir la colonne du tableau de bord. */
export const LIMITE_ACTIVITE_PAR_DEFAUT = 8;

/** Lit les `limite` dernières entrées d'activité ; les deux profils y ont accès. */
export function useActiviteRecente(limite: number = LIMITE_ACTIVITE_PAR_DEFAUT) {
  return useQuery({
    queryKey: [...clesRequetes.activite(), limite],
    queryFn: async () => {
      const { data, error } = await creerClientApi().GET('/activite', {
        params: { query: { limite } },
      });
      if (data === undefined) {
        throw erreurApi(error);
      }
      return data;
    },
  });
}
