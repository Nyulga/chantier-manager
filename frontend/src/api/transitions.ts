// Appel partagé de la transition d'une étape : utilisé par la page du chantier et par le tableau de bord.
import { creerClientApi } from './client';
import { erreurApi } from './erreurApi';
import type { components } from './schema';

/** Action de transition possible sur une étape. */
export type ActionTransition = components['schemas']['TransitionRequete']['action'];

/** Ce qu'il faut pour demander une transition ; le commentaire n'est utile qu'au refus. */
export type DemandeApiTransition = {
  readonly etapeId: string;
  readonly action: ActionTransition;
  readonly commentaire?: string | undefined;
};

/**
 * Demande à l'API de faire changer une étape de statut. C'est elle qui décide si c'est permis :
 * rien n'est vérifié ici, et son message d'erreur (403, 409, 422) est relevé tel quel.
 */
export async function transitionnerEtape({ etapeId, action, commentaire }: DemandeApiTransition) {
  const { data, error } = await creerClientApi().POST('/etapes/{etape_id}/transitions', {
    params: { path: { etape_id: etapeId } },
    body: commentaire === undefined ? { action } : { action, commentaire },
  });
  if (data === undefined) {
    throw erreurApi(error);
  }
  return data;
}
