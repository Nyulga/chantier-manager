// Violation volontaire : le type any est interdit.
export function lire(valeur: any): string {
  return String(valeur);
}
