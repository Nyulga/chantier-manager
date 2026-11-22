// Composant `LigneAValider` du design system Balise : une étape signalée terminée, avec ses actions.
import type { ReactNode, Ref } from 'react';

type LigneAValiderProps = {
  readonly titre: string;
  /** Le chantier de l'étape. */
  readonly contexte: string;
  /** Quand l'étape a été signalée terminée, déjà écrit (« Signalée hier à 17:42 »). */
  readonly signalement: string;
  /** Les boutons et liens d'action : seules les actions permises par l'API y figurent. */
  readonly actions: ReactNode;
  /**
   * Référence vers la ligne. La ligne est focalisable par programme (hors de l'ordre de
   * tabulation) : un écran peut y replacer le focus quand la ligne précédente disparaît.
   */
  readonly ref?: Ref<HTMLLIElement>;
};

/**
 * Ligne du `BlocAValider` : bord gauche rayé « balise » et fond `accent-soft` (Balise §4 et §5),
 * puis le titre et le chantier à gauche, le signalement au milieu et les actions à droite (elles
 * passent sous le texte sur mobile). Le texte reste en `fg` et `muted` : leur contraste sur
 * `accent-soft` dépasse 4,5:1 en clair comme en sombre.
 */
export function LigneAValider({ titre, contexte, signalement, actions, ref }: LigneAValiderProps) {
  return (
    <li ref={ref} tabIndex={-1} className="flex border-t border-line-soft bg-accent-soft">
      <div aria-hidden="true" className="rayures-balise w-rayure shrink-0" />
      <div className="flex min-w-0 flex-1 flex-wrap items-center gap-x-5 gap-y-3 px-5 py-4">
        <div className="flex min-w-0 flex-1 basis-full flex-col gap-1 tablette:basis-1/3">
          <p className="font-bold">{titre}</p>
          <p className="text-secondaire text-muted">{contexte}</p>
        </div>
        <p className="text-secondaire text-muted">{signalement}</p>
        <div className="flex w-full flex-col gap-2 tablette:w-auto tablette:flex-row">
          {actions}
        </div>
      </div>
    </li>
  );
}
