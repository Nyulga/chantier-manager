// Composant `Pile` du design system Balise : empile des éléments verticalement, avec un espacement.
import type { ReactNode } from 'react';

type EspacePile = 'moyen' | 'grand';

type PileProps = {
  readonly children: ReactNode;
  readonly espace?: EspacePile;
};

/** Espacements de l'échelle de Balise : 16 px et 24 px. */
const ESPACE_PAR_TAILLE: Record<EspacePile, string> = {
  moyen: 'gap-4',
  grand: 'gap-6',
};

/**
 * Une seule colonne, du mobile à l'ordinateur : la mise en page mobile d'abord suffit
 * au squelette, une grille s'ajoutera quand un écran en aura besoin.
 */
export function Pile({ children, espace = 'moyen' }: PileProps) {
  return <div className={`flex flex-col ${ESPACE_PAR_TAILLE[espace]}`}>{children}</div>;
}
