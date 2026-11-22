// Violation volontaire : une assertion de type avec as et une assertion de non-nullité avec !.
export function premier(valeurs: readonly string[]): string {
  const brut: unknown = valeurs[0];

  return (brut as string) + valeurs[1]!;
}
