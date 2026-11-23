// Appels partagés des chantiers : lus par les pages des chantiers, du tableau de bord, des étapes et la navigation.
import { clesRequetes } from './clesRequetes';
import { creerClientApi } from './client';
import { donneesOuErreur } from './erreurApi';

/**
 * Lit la liste des chantiers de l'API.
 *
 * Une fonctionnalité ne peut pas importer les hooks d'une autre (règle 05) : l'appel vit ici pour
 * que plusieurs hooks de `services` lisent la même ressource, sous la même clé de cache.
 */
export async function listerChantiers() {
  return donneesOuErreur(await creerClientApi().GET('/chantiers'));
}

/**
 * Clé de cache et appel de la liste, ensemble : les hooks qui lisent la liste (page des chantiers,
 * tableau de bord, navigation) la partagent ainsi à l'identique, avec un seul appel à l'API.
 */
export const optionsListeChantiers = {
  queryKey: clesRequetes.listeChantiers(),
  queryFn: listerChantiers,
};

/** Lit un chantier : ses informations, son avancement et le droit d'y ajouter une étape. */
export async function lireChantier(id: string) {
  return donneesOuErreur(
    await creerClientApi().GET('/chantiers/{chantier_id}', {
      params: { path: { chantier_id: id } },
    }),
  );
}
