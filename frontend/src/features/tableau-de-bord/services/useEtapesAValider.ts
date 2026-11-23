// Hook des étapes à valider : celles que les ouvriers ou les chefs ont signalées terminées.
import { useQuery } from '@tanstack/react-query';

import { clesRequetes } from '@/api/clesRequetes';
import { creerClientApi } from '@/api/client';
import { donneesOuErreur } from '@/api/erreurApi';
import { reessayerRequete } from '@/api/reessai';
import type { components } from '@/api/schema';

/** Étape qui attend une décision, avec la date de son dernier signalement. */
export type EtapeAValider = components['schemas']['EtapeAValiderReponse'];

/** En-tête par lequel l'API dit que la liste a été coupée à son plafond. */
const EN_TETE_LISTE_TRONQUEE = 'X-Liste-Tronquee';

/**
 * Liste les étapes à valider, de la plus ancienne à la plus récente (ordre de l'API), et dit si
 * l'API a coupé la liste (`tronquee`) : la pastille affiche alors « 50+ » au lieu d'un total faux.
 *
 * La requête n'est lancée que si l'API annonce le droit de lister (`autorisee`, venu de
 * `/api/moi`) : un ouvrier n'envoie jamais cette requête, et la section n'apparaît pas pour lui.
 */
export function useEtapesAValider(autorisee: boolean) {
  return useQuery({
    queryKey: clesRequetes.etapesAValider(),
    enabled: autorisee,
    // Un refus de l'API (403, 422…) n'est pas rejoué : la réponse serait la même.
    retry: reessayerRequete,
    queryFn: async () => {
      const resultat = await creerClientApi().GET('/etapes/a-valider');
      return {
        etapes: donneesOuErreur(resultat),
        tronquee: resultat.response.headers.get(EN_TETE_LISTE_TRONQUEE) === 'true',
      };
    },
  });
}
