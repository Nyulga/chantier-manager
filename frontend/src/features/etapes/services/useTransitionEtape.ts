// Hook de transition d'une étape : démarrer, signaler terminée, valider ou refuser.
import { useMutation, useQueryClient } from '@tanstack/react-query';

import { rafraichirApresTransition } from '@/api/rafraichissement';
import { transitionnerEtape } from '@/api/transitions';

import type { ActionEtape } from './useEtapes';

/** Type de l'erreur que lève la transition, pour le formulaire de refus qui affiche son champ. */
export type { ErreurApi } from '@/api/erreurApi';

/**
 * Demande de transition. Le commentaire n'est utile qu'au refus, où l'API l'exige (422 sinon).
 * La `version` est celle de l'étape affichée : l'API refuse (409) si l'étape a changé depuis.
 */
export type DemandeTransition = {
  readonly etapeId: string;
  /** Chantier de l'étape : il sert à relire ses données même quand l'API répond par une erreur. */
  readonly chantierId: string;
  readonly action: ActionEtape;
  readonly version: number;
  readonly commentaire?: string;
};

/**
 * Fait changer une étape de statut. C'est l'API qui décide si la transition est permise : le hook
 * transmet la demande sans rien vérifier. Le chantier, ses étapes et le tableau de bord sont relus
 * après chaque demande, réussie ou non : après un conflit (409), parce qu'un autre utilisateur a
 * agi, l'écran ne doit pas rester périmé.
 */
export function useTransitionEtape() {
  const clientRequetes = useQueryClient();

  return useMutation({
    mutationFn: ({ etapeId, action, version, commentaire }: DemandeTransition) =>
      transitionnerEtape({ etapeId, action, version, commentaire }),
    onSettled: (_etape, _erreur, demande) =>
      rafraichirApresTransition(clientRequetes, demande.chantierId),
  });
}
