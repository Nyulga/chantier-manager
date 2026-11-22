// Bloc ESLint des limites chiffrées contre le code spaghetti (règle 00, §4, et intent.md §3.1).
// Chaque seuil porte un nom : changer une limite demande un nouvel ADR.

/** Complexité cyclomatique maximale d'une fonction. */
const COMPLEXITE_MAX = 8;
/** Lignes de code maximales par fichier (commentaires et lignes vides non comptés). */
const LIGNES_PAR_FICHIER_MAX = 250;
/** Lignes de code maximales par fonction, composants compris. */
const LIGNES_PAR_FONCTION_MAX = 60;
/** Profondeur maximale d'imbrication des blocs. */
const PROFONDEUR_MAX = 3;
/** Paramètres maximaux d'une fonction : un composant reçoit un seul objet `props`. */
const PARAMETRES_MAX = 3;
/** Callbacks imbriqués au maximum. */
const CALLBACKS_IMBRIQUES_MAX = 3;

const SANS_COMMENTAIRES_NI_BLANCS = { skipBlankLines: true, skipComments: true };

export function blocLimites() {
  return {
    files: ['**/*.{ts,tsx}'],
    rules: {
      complexity: ['error', COMPLEXITE_MAX],
      'max-lines': ['error', { max: LIGNES_PAR_FICHIER_MAX, ...SANS_COMMENTAIRES_NI_BLANCS }],
      'max-lines-per-function': [
        'error',
        { max: LIGNES_PAR_FONCTION_MAX, ...SANS_COMMENTAIRES_NI_BLANCS },
      ],
      'max-depth': ['error', PROFONDEUR_MAX],
      'max-params': ['error', PARAMETRES_MAX],
      'max-nested-callbacks': ['error', CALLBACKS_IMBRIQUES_MAX],
    },
  };
}
