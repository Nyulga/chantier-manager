// Hook d'ajout d'une étape en fin de liste d'un chantier.
import { useMutation, useQueryClient } from '@tanstack/react-query';

import { creerClientApi } from '@/api/client';
import { donneesOuErreur } from '@/api/erreurApi';
import { rafraichirChantier } from '@/api/rafraichissement';

/** Type de l'erreur que lève l'ajout, pour le formulaire qui affiche ses erreurs par champ. */
export type { ErreurApi } from '@/api/erreurApi';

/**
 * Ajoute une étape (par son titre) au chantier. L'avancement baisse quand une étape s'ajoute :
 * on rafraîchit donc aussi le chantier et la liste, pas seulement les étapes. On les relit même
 * après un conflit (409) : une autre personne vient alors d'ajouter une étape, qui doit apparaître.
 */
export function useAjouterEtape(chantierId: string) {
  const clientRequetes = useQueryClient();

  return useMutation({
    mutationFn: async (titre: string) =>
      donneesOuErreur(
        await creerClientApi().POST('/chantiers/{chantier_id}/etapes', {
          params: { path: { chantier_id: chantierId } },
          body: { titre },
        }),
      ),
    onSettled: () => rafraichirChantier(clientRequetes, chantierId),
  });
}
