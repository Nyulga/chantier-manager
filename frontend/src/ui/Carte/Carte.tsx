// Composant `Carte` du design system Balise : un bloc de contenu sur fond `surface`.
import type { ReactNode } from 'react';

type CarteProps = {
  readonly children: ReactNode;
};

/**
 * Carte sans ombre : la hiérarchie passe par le fond et la bordure (Balise §4).
 * Elle empile son contenu avec un espacement de 12 px.
 */
export function Carte({ children }: CarteProps) {
  return (
    <div className="flex flex-col gap-3 rounded-controle border border-line bg-surface p-4">
      {children}
    </div>
  );
}
