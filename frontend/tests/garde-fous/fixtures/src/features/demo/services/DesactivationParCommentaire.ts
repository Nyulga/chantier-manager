// Violation volontaire : le commentaire de désactivation est ignoré, la violation reste signalée.
// eslint-disable-next-line @typescript-eslint/no-explicit-any
export function lire(valeur: any): string {
  return String(valeur);
}
