// Hook de transition d'une étape : démarrer, signaler terminée, valider ou refuser.
import { useMutation, useQueryClient } from '@tanstack/react-query';

import { creerClientApi } from '@/api/client';
import { erreurApi } from '@/api/erreurApi';

import { rafraichirChantier } from './rafraichirChantier';
import type { ActionEtape } from './useEtapes';

/** Demande de transition : le commentaire n'est utile qu'au refus, où l'API l'exige (422 sinon). */
export type DemandeTransition = {
  readonly etapeId: string;
  /** Chantier de l'étape : il sert à relire ses données même quand l'API répond par une erreur. */
  readonly chantierId: string;
  readonly action: ActionEtape;
  readonly commentaire?: string;
};

/**
 * Fait changer une étape de statut. C'est l'API qui décide si la transition est permise : le hook
 * transmet la demande sans rien vérifier. Le chantier et ses étapes sont relus après chaque
 * demande, réussie ou non : après un conflit (409), parce qu'un autre utilisateur a agi,
 * l'écran ne doit pas rester périmé.
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
    onSettled: (_etape, _erreur, demande) => rafraichirChantier(clientRequetes, demande.chantierId),
  });
}
