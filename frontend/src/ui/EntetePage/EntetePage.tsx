// Composant `EntetePage` du design system Balise : l'en-tête d'un écran, avec son titre de niveau 1.
import type { ReactNode } from 'react';

import { Titre } from '../Titre/Titre';

type EntetePageProps = {
  /** Petite étiquette au-dessus du titre, par exemple la date du jour. */
  readonly surtitre?: string;
  readonly titre: string;
  /** Les actions de la page (recherche, bouton de création…), alignées à droite sur ordinateur. */
  readonly children?: ReactNode;
};

/**
 * Surtitre en IBM Plex Mono et petites capitales, titre de page de niveau 1 (le seul de l'écran),
 * puis les actions qui passent à la ligne quand la place manque.
 */
export function EntetePage({ surtitre, titre, children }: EntetePageProps) {
  return (
    <header className="flex flex-wrap items-end justify-between gap-4">
      <div className="flex flex-col gap-1">
        {surtitre !== undefined && (
          <p className="font-mono text-etiquette tracking-etiquette text-muted uppercase">
            {surtitre}
          </p>
        )}
        <Titre niveau={1}>{titre}</Titre>
      </div>
      {children !== undefined && (
        <div className="flex flex-wrap items-center gap-3">{children}</div>
      )}
    </header>
  );
}
