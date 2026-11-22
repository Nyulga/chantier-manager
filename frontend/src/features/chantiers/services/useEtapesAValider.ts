// Hook des étapes à valider : celles que les ouvriers ont signalées terminées, pour le chef.
import { useQuery } from '@tanstack/react-query';

import { clesRequetes } from '@/api/clesRequetes';
import { creerClientApi } from '@/api/client';
import { AccesRefuseError, erreurApi } from '@/api/erreurApi';
import { reessayerRequete } from '@/api/reessai';
import type { components } from '@/api/schema';

/** Étape qui attend la décision d'un chef, avec la date de son dernier signalement. */
export type EtapeAValider = components['schemas']['EtapeAValiderReponse'];

/**
 * Liste les étapes à valider, de la plus ancienne à la plus récente (ordre de l'API).
 *
 * La requête part quel que soit le profil : l'API est seule juge du droit, et elle répond 403 à
 * qui n'est pas chef. L'écran masque alors la section (voir `estAccesRefuse`). Un 403 n'est pas
 * rejoué (voir `reessai.ts`) : la section serait masquée avec retard pour rien.
 */
export function useEtapesAValider() {
  return useQuery({
    queryKey: clesRequetes.etapesAValider(),
    retry: reessayerRequete,
    queryFn: async () => {
      const { data, error, response } = await creerClientApi().GET('/etapes/a-valider');
      if (data === undefined) {
        throw erreurApi(error, response.status);
      }
      return data;
    },
  });
}

/** Vrai si l'erreur est un refus 403 de l'API : la section n'est alors pas à afficher, sans message. */
export function estAccesRefuse(erreur: Error | null): boolean {
  return erreur instanceof AccesRefuseError;
}
