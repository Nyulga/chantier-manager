// Appels partagés des chantiers : lus par les pages des chantiers, du tableau de bord, des étapes et la navigation.
import { clesRequetes } from './clesRequetes';
import { creerClientApi } from './client';
import { donneesOuErreur } from './erreurApi';
import { reessayerRequete } from './reessai';
import type { components } from './schema';

/** Chantier tel que l'API le renvoie : budget `null` pour un ouvrier, avancement déjà calculé. */
export type Chantier = components['schemas']['ChantierReponse'];

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
 * Ce que la carte d'un chantier affiche, en valeurs simples : l'adresse est déjà mise à plat, et
 * ni le budget ni le client ne passent (ils sont réservés à la page du chantier). Rien n'est
 * calculé : avancement, compteurs, retard et nombre de jours sont ceux de l'API.
 */
export function resumerChantier(chantier: Chantier) {
  const { adresse } = chantier;
  return {
    id: chantier.id,
    nom: chantier.nom,
    adresse: `${adresse.voie}, ${adresse.code_postal} ${adresse.ville}`,
    etapesValidees: chantier.etapes_validees,
    etapesTotal: chantier.etapes_total,
    avancement: chantier.avancement,
    etapesAValider: chantier.etapes_a_valider,
    echeance: chantier.echeance,
    joursRestants: chantier.jours_restants,
    enRetard: chantier.en_retard,
  };
}

/** Résumé d'un chantier prêt pour la carte : voir `resumerChantier`. */
export type ChantierDeListe = ReturnType<typeof resumerChantier>;

/**
 * Options de lecture de la liste, partagées par les hooks qui la lisent (page des chantiers,
 * tableau de bord, navigation) : même clé de cache, un seul appel à l'API, et la même règle de
 * nouvelle tentative. Le compteur de la navigation remplace `select` pour ne garder que le nombre.
 * Les hooks reçoivent des résumés prêts pour la carte.
 */
export const optionsListeChantiers = {
  queryKey: clesRequetes.listeChantiers(),
  queryFn: listerChantiers,
  // Une liste refusée par l'API (403, 404) n'est pas rejouée : seules les pannes le sont.
  retry: reessayerRequete,
  select: (chantiers: readonly Chantier[]) => chantiers.map(resumerChantier),
};

/** Lit un chantier : ses informations, son avancement et le droit d'y ajouter une étape. */
export async function lireChantier(id: string) {
  return donneesOuErreur(
    await creerClientApi().GET('/chantiers/{chantier_id}', {
      params: { path: { chantier_id: id } },
    }),
  );
}
