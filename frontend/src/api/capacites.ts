// Appel partagé des capacités de l'acteur : ce que l'API l'autorise à faire, lu par plusieurs fonctionnalités.
import { creerClientApi } from './client';
import { donneesOuErreur } from './erreurApi';

/**
 * Lit `GET /api/moi`. Le frontend ne déduit aucun droit du profil choisi : il demande à l'API
 * ce que l'acteur peut faire (créer un chantier, lister les étapes à valider) et s'y tient.
 */
export async function lireCapacites() {
  return donneesOuErreur(await creerClientApi().GET('/moi'));
}
