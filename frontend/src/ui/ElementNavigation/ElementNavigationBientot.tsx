// Composant `ElementNavigationBientot` du design system Balise : une entrée de navigation pas encore disponible.
import type { ReactNode } from 'react';

import { Icone, type NomIcone } from '../Icone/Icone';
import { MentionBientot } from '../MentionBientot/MentionBientot';

type ElementNavigationBientotProps = {
  readonly icone: NomIcone;
  readonly children: ReactNode;
};

/**
 * Entrée désactivée : ce n'est pas un lien (`span` en `aria-disabled`), donc le clavier ne s'y
 * arrête pas. La mention « Bientôt » dit pourquoi, en toutes lettres : l'état désactivé ne
 * repose pas sur la seule couleur. Le texte est celui de la barre (`bg`), atténué par l'opacité :
 * `muted` serait trop sombre sur le graphite (contraste de 2,4:1 au lieu des 4,5:1 exigés).
 */
export function ElementNavigationBientot({ icone, children }: ElementNavigationBientotProps) {
  return (
    <li>
      <span
        aria-disabled="true"
        className="flex min-h-cible items-center gap-3 px-3 font-medium text-bg opacity-70"
      >
        <Icone nom={icone} />
        {children}
        <span className="ml-auto">
          <MentionBientot />
        </span>
      </span>
    </li>
  );
}
