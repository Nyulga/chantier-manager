// Appel partagé des étapes à valider : la liste et l'indication que l'API l'a coupée à son plafond.
import { creerClientApi } from './client';
import { donneesOuErreur } from './erreurApi';

/** En-tête par lequel l'API dit que la liste a été coupée à son plafond. */
const EN_TETE_LISTE_TRONQUEE = 'X-Liste-Tronquee';

/**
 * Lit `GET /api/etapes/a-valider`, de la plus ancienne à la plus récente (ordre de l'API), et dit
 * si l'API a coupé la liste (`tronquee`) : l'en-tête n'est lisible que sur la réponse, d'où cette
 * fonction d'appel plutôt qu'une lecture dans le hook.
 */
export async function listerEtapesAValider() {
  const resultat = await creerClientApi().GET('/etapes/a-valider');
  return {
    etapes: donneesOuErreur(resultat),
    tronquee: resultat.response.headers.get(EN_TETE_LISTE_TRONQUEE) === 'true',
  };
}
