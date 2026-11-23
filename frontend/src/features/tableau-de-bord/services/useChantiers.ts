// Hook de la liste des chantiers du tableau de bord : le nom des chantiers et l'aperçu « Mes chantiers ».
import { useQuery } from '@tanstack/react-query';

import { optionsListeChantiers } from '@/api/chantiers';
import type { components } from '@/api/schema';

/** Chantier tel que l'API le renvoie : avancement et compteurs déjà calculés. */
export type Chantier = components['schemas']['ChantierReponse'];

/**
 * Liste les chantiers que l'API renvoie à l'acteur. Elle partage sa clé de cache avec la liste de
 * la fonctionnalité « chantiers » : les deux écrans lisent la même donnée, avec un seul appel.
 */
export function useChantiers() {
  return useQuery(optionsListeChantiers);
}
