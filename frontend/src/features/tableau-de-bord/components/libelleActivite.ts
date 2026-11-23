// Libellés du fil d'activité : la phrase qui décrit chaque changement de statut d'une étape.
import type { EntreeActivite } from '../services/useActiviteRecente';

type Role = EntreeActivite['role'];

/** Ce que le fil affiche d'une entrée : qui, quoi (verbe compris) et les initiales de l'avatar. */
export type LibelleActivite = {
  readonly qui: string;
  readonly quoi: string;
  readonly initiales: string;
};

/**
 * Participe passé de chaque transition, selon le couple (ancien statut, nouveau statut) reçu de
 * l'API. On étend la table en ajoutant une ligne, pas un `if`. Ce n'est que de la présentation :
 * le frontend ne décide pas si une transition est valide, il l'écrit.
 */
const ACTION_PAR_TRANSITION: Readonly<Record<string, (titre: string) => string>> = {
  'a_faire>en_cours': (titre) => `démarré « ${titre} »`,
  'en_cours>terminee_a_valider': (titre) => `signalé « ${titre} » terminée`,
  'terminee_a_valider>validee': (titre) => `validé « ${titre} »`,
  'terminee_a_valider>en_cours': (titre) => `refusé « ${titre} »`,
};

/** Phrase de repli pour un couple de statuts que la table ne connaît pas. */
const ACTION_PAR_DEFAUT = (titre: string) => `modifié « ${titre} »`;

/** Le squelette n'a pas de comptes : on désigne la personne par son rôle. */
const NOM_PAR_ROLE: Readonly<Record<Role, string>> = {
  chef: 'Le chef',
  ouvrier: "L'ouvrier",
};

const INITIALES_PAR_ROLE: Readonly<Record<Role, string>> = { chef: 'CH', ouvrier: 'OU' };

/**
 * Écrit une entrée du fil. Si le rôle est celui du profil courant, la phrase s'adresse à
 * l'utilisateur (« Tu as validé ») ; sinon elle est à la troisième personne (« Le chef a validé »).
 * Le motif d'un refus est ajouté après la phrase, séparé par « : ».
 */
export function libelleActivite(entree: EntreeActivite, profil: Role): LibelleActivite {
  const cle = `${entree.ancien_statut}>${entree.nouveau_statut}`;
  const action = (ACTION_PAR_TRANSITION[cle] ?? ACTION_PAR_DEFAUT)(entree.titre_etape);
  const motif = entree.commentaire === null ? '' : ` : ${entree.commentaire}`;
  const estUtilisateur = entree.role === profil;

  return {
    qui: estUtilisateur ? 'Tu' : NOM_PAR_ROLE[entree.role],
    quoi: `${estUtilisateur ? 'as' : 'a'} ${action}${motif}`,
    initiales: INITIALES_PAR_ROLE[entree.role],
  };
}
