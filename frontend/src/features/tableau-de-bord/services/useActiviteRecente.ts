// Hook du fil d'activité : les derniers changements de statut d'étapes, du plus récent au plus ancien.
import { useQuery } from '@tanstack/react-query';

import { clesRequetes } from '@/api/clesRequetes';
import { creerClientApi } from '@/api/client';
import { donneesOuErreur } from '@/api/erreurApi';
import { reessayerRequete } from '@/api/reessai';
import type { components } from '@/api/schema';

/** Une entrée du fil : qui (le rôle) a fait passer quelle étape de quel statut à quel statut. */
export type EntreeActivite = components['schemas']['ActiviteReponse'];

/** Lit le fil d'activité. Sa taille est décidée par l'API : une seule valeur par défaut, la sienne. */
export function useActiviteRecente() {
  return useQuery({
    queryKey: clesRequetes.activite(),
    retry: reessayerRequete,
    queryFn: async () => donneesOuErreur(await creerClientApi().GET('/activite')),
  });
}
