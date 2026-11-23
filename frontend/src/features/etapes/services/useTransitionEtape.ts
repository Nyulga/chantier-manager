// Hook de transition d'une étape : démarrer, signaler terminée, valider ou refuser.
import { useMutation, useQueryClient } from '@tanstack/react-query';

import { rafraichirApresTransition } from '@/api/rafraichissement';
import { type DemandeTransition, transitionnerEtape } from '@/api/transitions';

/** Type de l'erreur que lève la transition, pour le formulaire de refus qui affiche son champ. */
export type { ErreurApi } from '@/api/erreurApi';

/**
 * Demande de transition de l'API, avec le chantier de l'étape : il sert à relire ses données même
 * quand l'API répond par une erreur.
 */
export type DemandeTransitionEtape = DemandeTransition & { readonly chantierId: string };

/**
 * Fait changer une étape de statut. C'est l'API qui décide si la transition est permise : le hook
 * transmet la demande sans rien vérifier. Le chantier, ses étapes et le tableau de bord sont relus
 * après chaque demande, réussie ou non : après un conflit (409), parce qu'un autre utilisateur a
 * agi, l'écran ne doit pas rester périmé.
 */
export function useTransitionEtape() {
  const clientRequetes = useQueryClient();

  return useMutation({
    mutationFn: ({ etapeId, action, version, commentaire }: DemandeTransitionEtape) =>
      transitionnerEtape({ etapeId, action, version, commentaire }),
    onSettled: (_etape, _erreur, demande) =>
      rafraichirApresTransition(clientRequetes, demande.chantierId),
  });
}
