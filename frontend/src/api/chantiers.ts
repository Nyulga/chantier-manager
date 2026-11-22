// Appel partagé de la liste des chantiers : lu par la page des chantiers, le tableau de bord et la navigation.
import { creerClientApi } from './client';
import { erreurApi } from './erreurApi';

/**
 * Lit la liste des chantiers de l'API.
 *
 * Une fonctionnalité ne peut pas importer les hooks d'une autre (règle 05) : l'appel vit ici pour
 * que plusieurs hooks de `services` lisent la même ressource, sous la même clé de cache.
 */
export async function listerChantiers() {
  const { data, error } = await creerClientApi().GET('/chantiers');
  if (data === undefined) {
    throw erreurApi(error);
  }
  return data;
}
