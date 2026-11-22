// Composant `Grille` du design system Balise : des éléments côte à côte quand la place le permet.
import { Children, type ReactNode } from 'react';

type GrilleProps = {
  readonly children: ReactNode;
};

/**
 * Liste en grille : une colonne sur mobile, deux dès que son conteneur dépasse 576 px (requête
 * de conteneur, et non de fenêtre : à 1024 px la colonne principale est étroite, car la barre
 * latérale et le fil d'activité occupent la place). Chaque enfant devient un élément de liste.
 */
export function Grille({ children }: GrilleProps) {
  return (
    <div className="@container">
      <ul className="grid grid-cols-1 gap-4 @xl:grid-cols-2">
        {Children.map(children, (enfant) => (
          <li>{enfant}</li>
        ))}
      </ul>
    </div>
  );
}
