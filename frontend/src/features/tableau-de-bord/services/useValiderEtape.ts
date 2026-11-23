// Hook de validation d'une étape depuis le tableau de bord (action « Valider » de la section « À valider »).
import { useMutation, useQueryClient } from '@tanstack/react-query';

import { rafraichirApresTransition } from '@/api/rafraichissement';
import { transitionnerEtape } from '@/api/transitions';

import type { EtapeAValider } from './useEtapesAValider';

/**
 * Valide l'étape reçue, en envoyant la version affichée. C'est l'API qui décide si c'est permis
 * (droits de l'acteur, étape bien « terminée »), et elle répond 409 si l'étape a changé depuis :
 * le message est alors affiché dans la section, avec le titre de l'étape. Les listes sont relues
 * après chaque demande, réussie ou non, pour que l'écran reflète ce que l'autre utilisateur a fait.
 */
export function useValiderEtape() {
  const clientRequetes = useQueryClient();

  return useMutation({
    mutationFn: (etape: EtapeAValider) =>
      transitionnerEtape({ etapeId: etape.id, action: 'valider', version: etape.version }),
    onSettled: (_etape, _erreur, etape) =>
      rafraichirApresTransition(clientRequetes, etape.chantier_id),
  });
}
