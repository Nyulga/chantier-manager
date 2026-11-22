// Formatage de la date du jour pour l'en-tête du tableau de bord : « dimanche 22 novembre 2026 ».

const FORMAT_LONG = new Intl.DateTimeFormat('fr-FR', {
  weekday: 'long',
  day: 'numeric',
  month: 'long',
  year: 'numeric',
});

/**
 * Écrit une date en toutes lettres, en français (jour de la semaine, jour, mois, année).
 *
 * Le premier du mois s'écrit « 1er » : la bibliothèque d'internationalisation du navigateur
 * ne le fait pas, on corrige donc ce seul cas. La mise en majuscules de l'étiquette est du
 * style, faite par le composant qui l'affiche : ici on garde l'orthographe française.
 */
export function formaterDateLongue(date: Date): string {
  return FORMAT_LONG.formatToParts(date)
    .map((partie) => (partie.type === 'day' && partie.value === '1' ? '1er' : partie.value))
    .join('');
}
