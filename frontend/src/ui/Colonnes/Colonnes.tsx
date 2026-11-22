// Composant `Colonnes` du design system Balise : une colonne principale et une colonne latérale.
import type { ReactNode } from 'react';

type ColonnesProps = {
  /** La colonne principale. */
  readonly children: ReactNode;
  readonly laterale: ReactNode;
};

/**
 * Sur mobile, la colonne latérale passe sous la principale (même ordre de lecture). Dès
 * l'ordinateur, elle se place à droite sur 300 px, la principale prenant le reste de la place.
 */
export function Colonnes({ children, laterale }: ColonnesProps) {
  return (
    <div className="flex flex-col gap-7 ordinateur:flex-row ordinateur:items-start">
      <div className="min-w-0 flex-1">{children}</div>
      <div className="min-w-0 ordinateur:w-colonne-laterale ordinateur:shrink-0">{laterale}</div>
    </div>
  );
}
