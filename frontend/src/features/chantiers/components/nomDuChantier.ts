// Recherche du nom d'un chantier dans la liste déjà chargée, pour les écrans qui ne reçoivent que son identifiant.
import type { Chantier } from '../services/useChantiers';

/** Nom affiché tant que la liste n'est pas chargée, ou si l'API ne renvoie plus ce chantier. */
const NOM_PAR_DEFAUT = 'Chantier';

/**
 * Les étapes à valider et l'activité ne portent que l'identifiant du chantier : on retrouve son nom
 * dans la liste des chantiers que la page a déjà chargée, plutôt que de refaire un appel par ligne.
 */
export function nomDuChantier(chantiers: readonly Chantier[] | undefined, id: string): string {
  return chantiers?.find((chantier) => chantier.id === id)?.nom ?? NOM_PAR_DEFAUT;
}
