// Composant `PuceChantier` du design system Balise : l'état de synthèse d'un chantier.
import type { ReactNode } from 'react';

/**
 * États d'un chantier :
 * - `a-valider` : des étapes attendent le chef (jaune, comme le reste de ce qui attend une action) ;
 * - `en-retard` : l'échéance est dépassée (fond et texte `danger`).
 */
type VariantePuce = 'a-valider' | 'en-retard';

type PuceChantierProps = {
  readonly variante: VariantePuce;
  /** Texte de la puce : l'état est toujours écrit en toutes lettres, jamais transmis par la couleur seule. */
  readonly children: ReactNode;
};

const CLASSES_PAR_VARIANTE: Record<VariantePuce, string> = {
  'a-valider': 'bg-statut-a-valider-fond text-statut-a-valider-texte',
  'en-retard': 'bg-danger-soft text-danger',
};

/** Puce de 6 px de rayon, en graisse 700, qui ne se coupe pas sur deux lignes. */
export function PuceChantier({ variante, children }: PuceChantierProps) {
  return (
    <span
      className={`inline-flex shrink-0 items-center rounded-badge px-3 py-1 text-badge font-bold whitespace-nowrap ${CLASSES_PAR_VARIANTE[variante]}`}
    >
      {children}
    </span>
  );
}
