// Règle de nouvelle tentative des requêtes de lecture, commune à toute l'application.
import { AccesRefuseError } from './erreurApi';

/** Nombre de tentatives de plus après un échec : c'est la valeur par défaut de TanStack Query. */
const NOMBRE_MAX_REESSAIS = 3;

/**
 * Dit si une requête en échec doit être rejouée. Un refus 403 ne l'est jamais : l'API répondra
 * la même chose, et chaque essai ferait attendre l'écran qui doit masquer la section refusée.
 * Les autres échecs (réseau coupé, panne passagère) sont rejoués, comme par défaut.
 */
export function reessayerRequete(echecs: number, erreur: Error): boolean {
  return !(erreur instanceof AccesRefuseError) && echecs < NOMBRE_MAX_REESSAIS;
}
