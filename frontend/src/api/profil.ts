// Profil courant du squelette : il n'y a pas encore d'authentification, l'utilisateur choisit
// s'il agit en « chef » ou en « ouvrier ». Le choix est gardé dans localStorage et envoyé à l'API
// dans l'en-tête `X-Profil` (voir `client.ts`). C'est l'API qui en tire les droits, jamais le frontend.
import type { components } from './schema';

/** Profils que l'API reconnaît : les rôles du schéma généré, pour ne jamais diverger de lui. */
export type Profil = components['schemas']['Role'];

/** Profil utilisé tant que l'utilisateur n'en a pas choisi un autre (ou si localStorage est inutilisable). */
export const PROFIL_PAR_DEFAUT: Profil = 'chef';

/** Clé de localStorage, préfixée par le nom de l'application pour éviter les collisions. */
export const CLE_PROFIL = 'chantier-manager.profil';

/** Événement interne qui prévient les composants du même onglet ; `storage` couvre les autres onglets. */
const EVENEMENT_PROFIL = 'chantier-manager:profil';

function estProfil(valeur: string | null): valeur is Profil {
  return valeur === 'chef' || valeur === 'ouvrier';
}

/**
 * Lit le profil courant.
 *
 * localStorage peut lever une exception (navigation privée, stockage désactivé par l'utilisateur) :
 * on retombe alors sur le profil par défaut plutôt que de casser toute l'application.
 * Une valeur inconnue (stockage modifié à la main) est ignorée pour la même raison.
 */
export function lireProfil(): Profil {
  try {
    const valeur = localStorage.getItem(CLE_PROFIL);
    return estProfil(valeur) ? valeur : PROFIL_PAR_DEFAUT;
  } catch {
    return PROFIL_PAR_DEFAUT;
  }
}

/** Enregistre le profil courant et prévient les écouteurs ; ne plante pas si le stockage échoue. */
export function enregistrerProfil(profil: Profil): void {
  try {
    localStorage.setItem(CLE_PROFIL, profil);
  } catch {
    // Le profil ne sera pas conservé au rechargement : la session reste utilisable.
  }
  window.dispatchEvent(new Event(EVENEMENT_PROFIL));
}

/**
 * Appelle `rappel` à chaque changement de profil, dans cet onglet comme dans les autres.
 *
 * Renvoie la fonction de désinscription. Elle a la forme attendue par `useSyncExternalStore`.
 */
export function ecouterProfil(rappel: () => void): () => void {
  window.addEventListener(EVENEMENT_PROFIL, rappel);
  window.addEventListener('storage', rappel);

  return () => {
    window.removeEventListener(EVENEMENT_PROFIL, rappel);
    window.removeEventListener('storage', rappel);
  };
}
