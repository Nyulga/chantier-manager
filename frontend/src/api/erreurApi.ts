// Traduction des erreurs de l'API en erreurs JavaScript dont le message est prêt à être affiché.

/** Message affiché quand l'API ne donne pas de détail exploitable. */
export const MESSAGE_ERREUR_PAR_DEFAUT = 'Une erreur est survenue. Réessaie dans un instant.';

/** Statut HTTP d'un refus de l'API : l'utilisateur est connu, mais n'a pas ce droit. */
const STATUT_ACCES_REFUSE = 403;

/**
 * Erreur d'une réponse 403. Elle porte le message de l'API comme toute autre erreur, mais se
 * reconnaît à son type : un écran peut alors masquer ce que l'API refuse, sans deviner de droit
 * à partir du profil, et la requête n'est pas rejouée (voir `reessai.ts`).
 */
export class AccesRefuseError extends Error {}

/**
 * Construit l'erreur à lever à partir du corps d'une réponse d'erreur (`application/problem+json`).
 * Si `statut` vaut 403, l'erreur est une `AccesRefuseError`.
 *
 * Le `detail` est écrit en français par l'API pour être montré tel quel à l'utilisateur. Le corps
 * n'est pas typé par OpenAPI : on le lit avec prudence, et on retombe sur un message neutre si
 * le détail manque ou n'est pas un texte (par exemple une erreur de proxy sans corps).
 */
export function erreurApi(corps: unknown, statut?: number): Error {
  const Type = statut === STATUT_ACCES_REFUSE ? AccesRefuseError : Error;
  if (typeof corps === 'object' && corps !== null && 'detail' in corps) {
    const { detail } = corps;
    if (typeof detail === 'string') {
      return new Type(detail);
    }
  }
  return new Type(MESSAGE_ERREUR_PAR_DEFAUT);
}
