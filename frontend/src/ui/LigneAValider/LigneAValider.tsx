// Composant `LigneAValider` du design system Balise : une étape signalée terminée, avec ses actions.
import type { ReactNode } from 'react';

import { Alerte } from '../Alerte/Alerte';

type LigneAValiderProps = {
  readonly titre: string;
  /** Le chantier de l'étape. */
  readonly contexte: string;
  /** Quand l'étape a été signalée terminée, déjà écrit (« Signalée hier à 17:42 »). */
  readonly signalement: string;
  /** Les boutons et liens d'action : seules les actions permises par l'API y figurent. */
  readonly actions: ReactNode;
  /** Message de l'API (409 par exemple), affiché sous la ligne, près de l'action. */
  readonly erreur?: string | undefined;
};

/**
 * Ligne du `BlocAValider` : titre et chantier à gauche, signalement au milieu, actions à droite
 * (elles passent sous le texte sur mobile). L'erreur de l'API s'affiche juste en dessous : une
 * alerte en haut de page resterait hors de l'écran sur mobile.
 */
export function LigneAValider({
  titre,
  contexte,
  signalement,
  actions,
  erreur,
}: LigneAValiderProps) {
  return (
    <li className="flex flex-col gap-3 border-t border-line-soft px-5 py-4">
      <div className="flex flex-wrap items-center gap-x-5 gap-y-3">
        <div className="flex min-w-0 flex-1 basis-full flex-col gap-1 tablette:basis-1/3">
          <p className="font-bold">{titre}</p>
          <p className="text-secondaire text-muted">{contexte}</p>
        </div>
        <p className="text-secondaire text-muted">{signalement}</p>
        <div className="flex w-full flex-col gap-2 tablette:w-auto tablette:flex-row">
          {actions}
        </div>
      </div>
      {erreur !== undefined && <Alerte variante="erreur">{erreur}</Alerte>}
    </li>
  );
}
