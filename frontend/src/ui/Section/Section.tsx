// Composant `Section` du design system Balise : une région de page nommée par son titre.
import { useId, type ReactNode, type Ref } from 'react';

import { Titre } from '../Titre/Titre';

type SectionProps = {
  readonly titre: string;
  /** Un lien ou une action alignés à droite du titre (« Voir les 4 chantiers »). */
  readonly action?: ReactNode;
  /** Rend le titre focalisable par programme : voir `Titre`. */
  readonly refTitre?: Ref<HTMLHeadingElement>;
  readonly children: ReactNode;
};

/**
 * Région (`<section>`) nommée par son titre de niveau 2 : les lecteurs d'écran peuvent
 * naviguer d'une section à l'autre. L'identifiant du titre est unique, plusieurs sections
 * peuvent donc coexister sur une page.
 */
export function Section({ titre, action, refTitre, children }: SectionProps) {
  const identifiantTitre = useId();

  return (
    <section aria-labelledby={identifiantTitre} className="flex flex-col gap-4">
      <div className="flex items-baseline justify-between gap-3">
        <div id={identifiantTitre}>
          <Titre niveau={2} refTitre={refTitre}>
            {titre}
          </Titre>
        </div>
        {action}
      </div>
      {children}
    </section>
  );
}
