// Composant `Bouton` du design system Balise : l'action que l'utilisateur déclenche.
import type { ReactNode } from 'react';

/**
 * Variantes de Balise (§5) :
 * - `principal` : l'action à mener (jaune sur mobile, graphite sur ordinateur) ;
 * - `secondaire` : une action annexe ;
 * - `danger` : un refus ou une action destructrice.
 */
type VarianteBouton = 'principal' | 'secondaire' | 'danger';

type BoutonProps = {
  readonly children: ReactNode;
  readonly variante?: VarianteBouton;
  readonly type?: 'button' | 'submit';
  readonly disabled?: boolean;
  /** Nom lu par les lecteurs d'écran quand plusieurs boutons portent le même libellé visible. */
  readonly libelleAccessible?: string;
  readonly onClick?: () => void;
};

const BASE =
  'inline-flex w-full items-center justify-center rounded-controle px-5 font-bold ' +
  'tablette:w-auto disabled:opacity-50';

const CLASSES_PAR_VARIANTE: Record<VarianteBouton, string> = {
  // Jaune réservé au bouton principal mobile (règle d'or de Balise) ; graphite dès l'ordinateur.
  principal:
    'min-h-cible-mobile-confort bg-accent text-on-accent ' +
    'ordinateur:min-h-cible ordinateur:bg-fg ordinateur:text-surface',
  secondaire: 'min-h-cible-mobile border border-line bg-surface text-fg ordinateur:min-h-cible',
  danger:
    'min-h-cible-mobile border-2 border-danger bg-transparent text-danger ordinateur:min-h-cible',
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
      className={`${BASE} ${CLASSES_PAR_VARIANTE[variante]}`}
    >
      {children}
    </button>
  );
}
