// Traduction des erreurs de l'API en erreurs JavaScript dont le message est prêt à être affiché.
import type { components } from './schema';

/** Message affiché quand l'API ne donne pas de détail exploitable. */
export const MESSAGE_ERREUR_PAR_DEFAUT = 'Une erreur est survenue. Réessaie dans un instant.';

/**
 * Messages de repli, par statut, pour les refus dont la réponse n'a pas de détail exploitable :
 * le proxy (Caddy) ou un pare-feu répond parfois à la place de l'API, sans corps `problem+json`.
 * Quand l'API a répondu, c'est toujours son `detail` qui s'affiche.
 */
const MESSAGES_PAR_STATUT: Readonly<Record<number, string>> = {
  413: 'Ta demande est trop volumineuse.',
  429: 'Trop de demandes. Réessaie dans quelques instants.',
};

/** Statut HTTP d'une ressource que l'API ne connaît pas (ou que l'acteur n'a pas le droit de voir). */
const STATUT_INTROUVABLE = 404;

/** Une erreur de saisie attachée à un champ : `champ` est un chemin pointé (`adresse.code_postal`). */
export type ErreurChamp = components['schemas']['ErreurChampReponse'];

/**
 * Erreur renvoyée par l'API, ou par le réseau quand elle n'a pas répondu (alors sans statut).
 *
 * Elle porte le message à afficher et, pour un 422, les erreurs par champ : les formulaires les
 * montrent sous chaque champ plutôt que dans une alerte unique. Les écrans n'importent jamais cette
 * classe (ils ne peuvent pas toucher à `src/api`) : ils utilisent ses méthodes sur l'erreur que
 * leur renvoie un hook.
 */
export class ErreurApi extends Error {
  readonly statut: number | undefined;
  readonly erreurs: readonly ErreurChamp[];

  constructor(message: string, statut?: number, erreurs: readonly ErreurChamp[] = []) {
    super(message);
    this.statut = statut;
    this.erreurs = erreurs;
  }

  /** Vrai pour une réponse 404 : la page affiche alors « introuvable » plutôt qu'une alerte. */
  get introuvable(): boolean {
    return this.statut === STATUT_INTROUVABLE;
  }

  /** Premier message de l'API pour ce champ, ou `undefined` si le champ n'est pas en cause. */
  messageDuChamp(champ: string): string | undefined {
    return this.erreurs.find((erreur) => erreur.champ === champ)?.message;
  }

  /**
   * Message pour l'alerte globale du formulaire : ce que les champs affichés ne montrent pas.
   *
   * Sans erreur par champ (une règle qui touche plusieurs champs, un 409, une panne), c'est le
   * détail de l'API. Sinon, ce sont les messages des champs que le formulaire n'a pas : aucun
   * message ne se perd. Quand chaque message a son champ, il n'y a pas d'alerte en plus.
   */
  messageGlobal(champsAffiches: readonly string[]): string | undefined {
    if (this.erreurs.length === 0) {
      return this.message;
    }
    const sansChamp = this.erreurs.filter((erreur) => !champsAffiches.includes(erreur.champ));
    return sansChamp.length === 0 ? undefined : sansChamp.map(({ message }) => message).join(' ');
  }
}

/*
 * Toute requête échoue avec une `ErreurApi` (voir `donneesOuErreur` et `client.ts`) : TanStack
 * Query type donc `error` en conséquence, et les écrans lisent `erreurs` sans conversion.
 */
declare module '@tanstack/react-query' {
  interface Register {
    defaultError: ErreurApi;
  }
}

/** Message à afficher quand la réponse n'a pas de détail : celui du statut s'il en a un, sinon le neutre. */
function messageParDefaut(statut: number | undefined): string {
  return (
    (statut === undefined ? undefined : MESSAGES_PAR_STATUT[statut]) ?? MESSAGE_ERREUR_PAR_DEFAUT
  );
}

function estErreurChamp(valeur: unknown): valeur is ErreurChamp {
  return (
    typeof valeur === 'object' &&
    valeur !== null &&
    'champ' in valeur &&
    typeof valeur.champ === 'string' &&
    'message' in valeur &&
    typeof valeur.message === 'string'
  );
}

/**
 * Construit l'erreur à lever à partir du corps d'une réponse d'erreur (`application/problem+json`).
 *
 * Le `detail` est écrit en français par l'API pour être montré tel quel à l'utilisateur. Le corps
 * n'est pas typé par OpenAPI : on le lit avec prudence, et on retombe sur un message neutre si
 * le détail manque ou n'est pas un texte (par exemple une erreur de proxy sans corps), propre au
 * statut pour un 413 ou un 429. Les
 * entrées de `erreurs` mal formées sont ignorées.
 */
export function erreurApi(corps: unknown, statut?: number): ErreurApi {
  const messageDeRepli = messageParDefaut(statut);
  if (typeof corps !== 'object' || corps === null) {
    return new ErreurApi(messageDeRepli, statut);
  }
  const detail = 'detail' in corps && typeof corps.detail === 'string' ? corps.detail : undefined;
  const erreurs = 'erreurs' in corps && Array.isArray(corps.erreurs) ? corps.erreurs : [];
  return new ErreurApi(detail ?? messageDeRepli, statut, erreurs.filter(estErreurChamp));
}

/**
 * Renvoie les données d'une réponse réussie, ou lève l'erreur de l'API. C'est le motif commun de
 * tous les appels : le client renvoie `data` ou `error`, jamais les deux.
 *
 * Lève :
 *     ErreurApi : la réponse n'a pas de données ; elle porte le statut et les erreurs par champ.
 */
export function donneesOuErreur<Donnees>(resultat: {
  readonly data?: Donnees | undefined;
  readonly error?: unknown;
  readonly response: Response;
}): Donnees {
  if (resultat.data === undefined) {
    throw erreurApi(resultat.error, resultat.response.status);
  }
  return resultat.data;
}
