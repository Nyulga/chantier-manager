// Composant `Texte` du design system Balise : paragraphes et données de l'interface.
import type { ReactNode } from 'react';

/**
 * Variantes typographiques de Balise (§3) :
 * - `courant` : texte principal ;
 * - `secondaire` : métadonnées, en gris.
 */
type VarianteTexte = 'courant' | 'secondaire';

type TexteProps = {
  readonly children: ReactNode;
  readonly variante?: VarianteTexte;
};

const CLASSES_PAR_VARIANTE: Record<VarianteTexte, string> = {
  courant: 'text-texte',
  secondaire: 'text-secondaire text-muted',
};

/** Paragraphe de texte, dans la variante demandée (courante par défaut). */
export function Texte({ children, variante = 'courant' }: TexteProps) {
  return <p className={CLASSES_PAR_VARIANTE[variante]}>{children}</p>;
}
