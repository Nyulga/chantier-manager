// Violation volontaire : quatre niveaux de blocs imbriqués (la limite est de trois),
// et quatre callbacks imbriqués (la limite est de trois).
export function profondeur(a: boolean, b: boolean, c: boolean, d: boolean): number {
  if (a) {
    if (b) {
      if (c) {
        if (d) {
          return 1;
        }
      }
    }
  }
  return 0;
}

export const callbacks = [1].map(() => [2].map(() => [3].map(() => [4].map(() => 5))));
