// Traduction des erreurs de l'API en erreurs JavaScript dont le message est prêt à être affiché.

/** Message affiché quand l'API ne donne pas de détail exploitable. */
export const MESSAGE_ERREUR_PAR_DEFAUT = 'Une erreur est survenue. Réessaie dans un instant.';

/**
 * Construit l'erreur à lever à partir du corps d'une réponse d'erreur (`application/problem+json`).
 *
 * Le `detail` est écrit en français par l'API pour être montré tel quel à l'utilisateur. Le corps
 * n'est pas typé par OpenAPI : on le lit avec prudence, et on retombe sur un message neutre si
 * le détail manque ou n'est pas un texte (par exemple une erreur de proxy sans corps).
 */
export function erreurApi(corps: unknown): Error {
  if (typeof corps === 'object' && corps !== null && 'detail' in corps) {
    const { detail } = corps;
    if (typeof detail === 'string') {
      return new Error(detail);
    }
  }
  return new Error(MESSAGE_ERREUR_PAR_DEFAUT);
}
