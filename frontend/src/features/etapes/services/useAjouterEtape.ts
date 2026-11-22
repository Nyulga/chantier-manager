// Hook d'ajout d'une étape en fin de liste d'un chantier.
import { useMutation, useQueryClient } from '@tanstack/react-query';

import { creerClientApi } from '@/api/client';
import { erreurApi } from '@/api/erreurApi';
import { rafraichirChantier } from '@/api/rafraichissement';

/**
 * Ajoute une étape (par son titre) au chantier. L'avancement baisse quand une étape s'ajoute :
 * on rafraîchit donc aussi le chantier et la liste, pas seulement les étapes.
 */
export function useAjouterEtape(chantierId: string) {
  const clientRequetes = useQueryClient();

  return useMutation({
    mutationFn: async (titre: string) => {
      const { data, error } = await creerClientApi().POST('/chantiers/{chantier_id}/etapes', {
        params: { path: { chantier_id: chantierId } },
        body: { titre },
      });
      if (data === undefined) {
        throw erreurApi(error);
      }
      return data;
    },
    onSuccess: () => rafraichirChantier(clientRequetes, chantierId),
  });
}
