// Hook des étapes à valider : celles que les ouvriers ont signalées terminées, pour le chef.
import { useQuery } from '@tanstack/react-query';

import { clesRequetes } from '@/api/clesRequetes';
import { creerClientApi } from '@/api/client';
import { erreurApi } from '@/api/erreurApi';
import type { components } from '@/api/schema';

import { useProfilCourant } from './useProfilCourant';

/** Étape qui attend la décision d'un chef, avec la date de son dernier signalement. */
export type EtapeAValider = components['schemas']['EtapeAValiderReponse'];

/**
 * Liste les étapes à valider, de la plus ancienne à la plus récente (ordre de l'API).
 *
 * L'API réserve cette liste au chef (403 pour un ouvrier) : la requête n'est donc pas envoyée
 * pour un ouvrier. Ce n'est pas un droit déduit côté client (l'API reste seule juge) : on évite
 * seulement un appel dont on connaît déjà la réponse.
 */
export function useEtapesAValider() {
  const profil = useProfilCourant();

  return useQuery({
    queryKey: clesRequetes.etapesAValider(),
    enabled: profil === 'chef',
    queryFn: async () => {
      const { data, error } = await creerClientApi().GET('/etapes/a-valider');
      if (data === undefined) {
        throw erreurApi(error);
      }
      return data;
    },
  });
}
