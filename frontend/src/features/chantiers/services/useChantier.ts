// Hook d'un chantier : ses informations et son avancement, tels que l'API les renvoie.
import { useQuery } from '@tanstack/react-query';

import { clesRequetes } from '@/api/clesRequetes';
import { lireChantier } from '@/api/chantiers';
import { reessayerRequete } from '@/api/reessai';

/** Consulte un chantier. Un chantier inconnu donne une erreur 404 de l'API (`error.introuvable`). */
export function useChantier(id: string) {
  return useQuery({
    queryKey: clesRequetes.chantier(id),
    // Un 404 n'est pas rejoué : la page « introuvable » doit s'afficher tout de suite.
    retry: reessayerRequete,
    queryFn: () => lireChantier(id),
  });
}
