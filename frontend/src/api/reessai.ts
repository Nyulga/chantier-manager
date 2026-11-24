// Règle de nouvelle tentative des requêtes de lecture, posée une seule fois dans les options par défaut
// du client de requêtes (`src/app/providers.tsx`) : aucun hook ne peut l'oublier, alors que la valeur
// par défaut de TanStack Query rejoue même un 403 ou un 404. Le client des tests la reprend aussi.
import type { ErreurApi } from './erreurApi';

/** Nombre de tentatives de plus après un échec : c'est la valeur par défaut de TanStack Query. */
const NOMBRE_MAX_REESSAIS = 3;

/** Premier statut HTTP d'une erreur du client, et premier d'une erreur du serveur. */
const PREMIER_STATUT_CLIENT = 400;
const PREMIER_STATUT_SERVEUR = 500;

/**
 * Dit si une requête en échec doit être rejouée. Une réponse de l'API qui refuse (403, 404, 422…)
 * ne l'est jamais : elle répondrait la même chose, et chaque essai ferait attendre l'écran qui
 * doit afficher l'erreur ou la page introuvable. Les pannes (réseau coupé, 5xx) sont rejouées.
 */
export function reessayerRequete(echecs: number, erreur: ErreurApi): boolean {
  const { statut } = erreur;
  const reponseDefinitive =
    statut !== undefined && statut >= PREMIER_STATUT_CLIENT && statut < PREMIER_STATUT_SERVEUR;
  return !reponseDefinitive && echecs < NOMBRE_MAX_REESSAIS;
}
