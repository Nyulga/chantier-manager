// Formatage des montants pour l'affichage : euros à la française, par exemple « 18 450,00 € ».

const FORMAT_EUROS = new Intl.NumberFormat('fr-FR', { style: 'currency', currency: 'EUR' });

const DECIMAL = /^-?\d+(\.\d+)?$/;

/** Reconnaît un nombre décimal écrit en chiffres : le seul texte que `Intl.NumberFormat` accepte. */
function estDecimal(texte: string): texte is `${number}` {
  return DECIMAL.test(texte);
}

/**
 * Met en forme le montant décimal que renvoie l'API (`"18450.00"`).
 *
 * La chaîne est transmise telle quelle à `Intl.NumberFormat`, qui sait lire un nombre décimal
 * exact : on ne passe jamais par un `number` (flottant), qui perdrait des centimes sur les
 * grands montants. Le frontend ne calcule rien, il met seulement en forme. Un texte qui n'est
 * pas un décimal est rendu tel quel plutôt que d'afficher « NaN ».
 */
export function formaterMontant(montant: string): string {
  return estDecimal(montant) ? FORMAT_EUROS.format(montant) : montant;
}
