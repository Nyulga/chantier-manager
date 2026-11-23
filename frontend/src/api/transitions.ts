// Appel partagé de la transition d'une étape : utilisé par la page du chantier et par le tableau de bord.
import { creerClientApi } from './client';
import { donneesOuErreur } from './erreurApi';
import type { components } from './schema';

/** Action de transition possible sur une étape. */
export type ActionTransition = components['schemas']['TransitionRequete']['action'];

/**
 * Ce qu'il faut pour demander une transition. Le commentaire n'est utile qu'au refus. La `version`
 * est celle de l'étape que l'écran affichait : si l'étape a changé depuis, l'API répond 409
 * plutôt que de décider sur un état périmé.
 */
export type DemandeTransition = {
  readonly etapeId: string;
  readonly action: ActionTransition;
  readonly version: number;
  readonly commentaire?: string | undefined;
};

/**
 * Demande à l'API de faire changer une étape de statut. C'est elle qui décide si c'est permis :
 * rien n'est vérifié ici, et son message d'erreur (403, 409, 422) est relevé tel quel.
 */
export async function transitionnerEtape({
  etapeId,
  action,
  version,
  commentaire,
}: DemandeTransition) {
  return donneesOuErreur(
    await creerClientApi().POST('/etapes/{etape_id}/transitions', {
      params: { path: { etape_id: etapeId } },
      body: commentaire === undefined ? { action, version } : { action, version, commentaire },
    }),
  );
}
