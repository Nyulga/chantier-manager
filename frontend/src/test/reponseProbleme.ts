// Aide de test : la réponse d'erreur de l'API (RFC 9457, `application/problem+json`), prête pour MSW.
import { HttpResponse } from 'msw';

/** Une erreur de saisie attachée à un champ, telle que l'API la renvoie dans un 422. */
type ErreurChamp = { readonly champ: string; readonly message: string };

/**
 * Construit la réponse d'erreur de l'API. `erreurs` n'est ajouté que si le test en donne : seul le
 * 422 en porte, les autres erreurs n'ont que `detail`.
 */
export function reponseProbleme(status: number, detail: string, erreurs?: readonly ErreurChamp[]) {
  return HttpResponse.json(
    { status, title: detail, type: 'about:blank', detail, ...(erreurs && { erreurs }) },
    { status, headers: { 'Content-Type': 'application/problem+json' } },
  );
}
