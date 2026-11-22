// Hook de transition d'une étape : démarrer, signaler terminée, valider ou refuser.
import { useMutation, useQueryClient } from '@tanstack/react-query';

import { creerClientApi } from '@/api/client';
import { erreurApi } from '@/api/erreurApi';

import { rafraichirChantier } from './rafraichirChantier';
import type { ActionEtape } from './useEtapes';

/** Demande de transition : le commentaire n'est utile qu'au refus, où l'API l'exige (422 sinon). */
export type DemandeTransition = {
  readonly etapeId: string;
  readonly action: ActionEtape;
  readonly commentaire?: string;
};

/**
 * Fait changer une étape de statut. C'est l'API qui décide si la transition est permise : le hook
 * transmet la demande sans rien vérifier. L'étape renvoyée donne le chantier à rafraîchir
 * (validation et refus changent son avancement).
 */
export function useTransitionEtape() {
  const clientRequetes = useQueryClient();

  return useMutation({
    mutationFn: async ({ etapeId, action, commentaire }: DemandeTransition) => {
      const { data, error } = await creerClientApi().POST('/etapes/{etape_id}/transitions', {
        params: { path: { etape_id: etapeId } },
        body: commentaire === undefined ? { action } : { action, commentaire },
      });
      if (data === undefined) {
        throw erreurApi(error);
      }
      return data;
    },
    onSuccess: (etape) => rafraichirChantier(clientRequetes, etape.chantier_id),
  });
}
