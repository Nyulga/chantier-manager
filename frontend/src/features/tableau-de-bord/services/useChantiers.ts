// Hook de la liste des chantiers du tableau de bord : le nom des chantiers et l'aperçu « Mes chantiers ».
import { useQuery } from '@tanstack/react-query';

import { optionsListeChantiers } from '@/api/chantiers';

/** Chantier de la liste, réduit à ce que sa carte affiche : avancement et compteurs viennent de l'API. */
export type { ChantierDeListe } from '@/api/chantiers';

/**
 * Liste les chantiers que l'API renvoie à l'acteur. Elle partage sa clé de cache avec la liste de
 * la fonctionnalité « chantiers » : les deux écrans lisent la même donnée, avec un seul appel.
 */
export function useChantiers() {
  return useQuery(optionsListeChantiers);
}
