// Composant `Bouton` du design system Balise : l'action que l'utilisateur déclenche.
import type { ReactNode } from 'react';

import { classesBouton, type VarianteBouton } from './classesBouton';

type BoutonProps = {
  readonly children: ReactNode;
  readonly variante?: VarianteBouton;
  readonly type?: 'button' | 'submit';
  readonly disabled?: boolean;
  /** Nom lu par les lecteurs d'écran quand plusieurs boutons portent le même libellé visible. */
  readonly libelleAccessible?: string;
  readonly onClick?: () => void;
};

/**
 * Bouton de type « button » par défaut : un bouton sans type enverrait le formulaire qui
 * le contient. Seul un bouton `submit` déclenche l'envoi.
 */
export function Bouton({
  children,
  variante = 'principal',
  type = 'button',
  disabled = false,
  libelleAccessible,
  onClick,
}: BoutonProps) {
  return (
    <button
      type={type}
      disabled={disabled}
      aria-label={libelleAccessible}
      onClick={onClick}
      className={classesBouton(variante)}
    >
      {children}
    </button>
  );
}
