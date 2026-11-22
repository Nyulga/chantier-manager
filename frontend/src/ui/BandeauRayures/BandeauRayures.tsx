// Composant `BandeauRayures` du design system Balise : le bandeau « balise » en haut du bloc « À valider ».

/**
 * Bandeau de 8 px aux rayures jaunes et graphite (Balise §4).
 *
 * Les rayures et le jaune sont réservés à ce qui attend une action du chef (règle d'or) : ce
 * bandeau ne sert qu'en haut du bloc « À valider ». Il est purement décoratif, donc caché des
 * lecteurs d'écran.
 */
export function BandeauRayures() {
  return <div aria-hidden="true" className="rayures-balise h-rayure w-full" />;
}
