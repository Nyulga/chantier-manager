// Formatage du délai avant l'échéance d'un chantier : « J-54 » ou « En retard de 4 jours ».

type Delai = {
  /** Nombre de jours, toujours positif ou nul : le temps restant, ou le retard si `enRetard`. */
  readonly joursRestants: number;
  readonly enRetard: boolean;
};

/**
 * Met en forme le délai que l'API a calculé. Le frontend ne compare jamais de dates : le retard
 * et le nombre de jours viennent de l'API, ce formatage ne fait que choisir les mots.
 */
export function formaterDelai({ joursRestants, enRetard }: Delai): string {
  if (enRetard) {
    return `En retard de ${String(joursRestants)} ${joursRestants >= 2 ? 'jours' : 'jour'}`;
  }
  return joursRestants === 0 ? "Aujourd'hui" : `J-${String(joursRestants)}`;
}
