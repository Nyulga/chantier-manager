// Violation volontaire : une fonction de complexité cyclomatique 9 (la limite est de 8).
export function classer(n: number): string {
  if (n === 1) return 'un';
  if (n === 2) return 'deux';
  if (n === 3) return 'trois';
  if (n === 4) return 'quatre';
  if (n === 5) return 'cinq';
  if (n === 6) return 'six';
  if (n === 7) return 'sept';
  if (n === 8) return 'huit';
  return 'autre';
}
