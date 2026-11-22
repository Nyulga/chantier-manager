// Hook du compteur « Mes chantiers » de la navigation : le nombre de chantiers que l'API renvoie.
import { useQuery } from '@tanstack/react-query';

import { listerChantiers } from '@/api/chantiers';
import { clesRequetes } from '@/api/clesRequetes';

/**
 * Renvoie le nombre de chantiers, ou `undefined` tant que la liste n'est pas chargée (ou si
 * l'API échoue : la navigation n'affiche alors pas de compteur plutôt qu'un faux zéro).
 *
 * Il lit la même clé que la liste des chantiers : les deux partagent un seul appel et un seul cache.
 */
export function useNombreChantiers(): number | undefined {
  const { data } = useQuery({
    queryKey: clesRequetes.listeChantiers(),
    queryFn: listerChantiers,
    select: (chantiers) => chantiers.length,
  });

  return data;
}
