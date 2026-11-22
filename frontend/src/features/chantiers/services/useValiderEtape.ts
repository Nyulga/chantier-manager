// Hook de validation d'une étape depuis le tableau de bord (action « Valider » de la section « À valider »).
import { useMutation, useQueryClient } from '@tanstack/react-query';

import { rafraichirApresTransition } from '@/api/rafraichissement';
import { transitionnerEtape } from '@/api/transitions';

import type { EtapeAValider } from './useEtapesAValider';

/**
 * Valide l'étape reçue. C'est l'API qui décide si c'est permis (chef affecté, étape bien
 * « terminée »), et elle répond 409 si l'étape a déjà changé : le message est alors affiché
 * près du bouton. Les listes sont relues après chaque demande, réussie ou non, pour que l'écran
 * reflète ce que l'autre utilisateur a fait.
 */
export function useValiderEtape() {
  const clientRequetes = useQueryClient();

  return useMutation({
    mutationFn: (etape: EtapeAValider) =>
      transitionnerEtape({ etapeId: etape.id, action: 'valider' }),
    onSettled: (_etape, _erreur, etape) =>
      rafraichirApresTransition(clientRequetes, etape.chantier_id),
  });
}
