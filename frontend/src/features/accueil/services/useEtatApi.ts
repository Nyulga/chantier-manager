// Hook de l'état de l'API : interroge `/api/health` pour savoir si le serveur répond.
import { useQuery } from '@tanstack/react-query';

import { creerClientApi } from '@/api/client';

/**
 * Interroge la route de santé de l'API et renvoie le résultat TanStack Query.
 *
 * Toute réponse sans corps (erreur HTTP) ou toute panne réseau devient une erreur de la requête,
 * pour que la page n'ait qu'un seul cas « indisponible » à gérer. Aucune nouvelle tentative :
 * un état de santé doit refléter la réalité tout de suite, pas après plusieurs essais.
 */
export function useEtatApi() {
  return useQuery({
    queryKey: ['etat-api'],
    retry: false,
    queryFn: async () => {
      const { data } = await creerClientApi().GET('/health');
      if (data === undefined) {
        throw new Error("L'API a répondu par une erreur.");
      }
      return data;
    },
  });
}
