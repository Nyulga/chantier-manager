// Hook de la liste des étapes d'un chantier, avec les actions que l'acteur peut faire sur chacune.
import { useQuery } from '@tanstack/react-query';

import { clesRequetes } from '@/api/clesRequetes';
import { creerClientApi } from '@/api/client';
import { donneesOuErreur } from '@/api/erreurApi';
import { reessayerRequete } from '@/api/reessai';
import type { components } from '@/api/schema';

/** Étape telle que l'API la renvoie, avec ses `actions_permises` : seules elles ont un bouton. */
export type Etape = components['schemas']['EtapeReponse'];

/** Action de transition possible sur une étape. */
export type ActionEtape = Etape['actions_permises'][number];

/** Liste les étapes d'un chantier, dans l'ordre de l'API. */
export function useEtapes(chantierId: string) {
  return useQuery({
    queryKey: clesRequetes.etapes(chantierId),
    retry: reessayerRequete,
    queryFn: async () =>
      donneesOuErreur(
        await creerClientApi().GET('/chantiers/{chantier_id}/etapes', {
          params: { path: { chantier_id: chantierId } },
        }),
      ),
  });
}
