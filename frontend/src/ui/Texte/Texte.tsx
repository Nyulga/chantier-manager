// Composant `Texte` du design system Balise : paragraphes et données de l'interface.
import type { ReactNode } from 'react';

/**
 * Variantes typographiques de Balise (§3) :
 * - `courant` : texte principal ;
 * - `secondaire` : métadonnées, en gris ;
 * - `etiquette` : petites étiquettes de 12 px ;
 * - `donnee` : références et horodatages, en IBM Plex Mono.
 */
type VarianteTexte = 'courant' | 'secondaire' | 'etiquette' | 'donnee';

type TexteProps = {
  readonly children: ReactNode;
  readonly variante?: VarianteTexte;
};

const CLASSES_PAR_VARIANTE: Record<VarianteTexte, string> = {
  courant: 'text-texte',
  secondaire: 'text-secondaire text-muted',
  etiquette: 'text-etiquette font-semibold text-muted',
  // Les chiffres alignés facilitent la lecture des références et des dates.
  donnee: 'font-mono text-secondaire tabular-nums',
};

/** Paragraphe de texte, dans la variante demandée (courante par défaut). */
export function Texte({ children, variante = 'courant' }: TexteProps) {
  return <p className={CLASSES_PAR_VARIANTE[variante]}>{children}</p>;
}
