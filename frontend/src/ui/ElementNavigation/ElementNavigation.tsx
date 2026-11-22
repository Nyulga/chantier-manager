// Composant `ElementNavigation` du design system Balise : un lien de la barre latérale.
import type { ReactNode } from 'react';
import { NavLink } from 'react-router';

import { Icone, type NomIcone } from '../Icone/Icone';

type ElementNavigationProps = {
  readonly vers: string;
  readonly icone: NomIcone;
  readonly children: ReactNode;
  /**
   * Actif seulement sur l'adresse exacte. Sans lui, l'élément reste actif sur les pages
   * enfants (« Mes chantiers » l'est aussi sur le détail d'un chantier).
   */
  readonly exact?: boolean;
  readonly compteur?: number | undefined;
};

/*
 * Le contour du focus passe en `bg` : la barre est graphite (couleur `fg`), et le contour
 * global, de la couleur `fg`, y serait invisible.
 */
const CLASSES_COMMUNES =
  'flex min-h-cible items-center gap-3 rounded-controle px-3 ' + 'focus-visible:outline-bg';

/** Actif : fond `accent` (la navigation active fait partie des usages prévus du jaune, Balise §1). */
const CLASSES_ACTIF = 'bg-accent font-bold text-on-accent';

const CLASSES_INACTIF = 'font-medium text-bg hover:bg-muted';

/**
 * Lien de navigation dans la barre latérale. `NavLink` compare l'adresse courante à `vers`
 * et pose `aria-current="page"` sur l'élément actif : l'état n'est donc pas porté par la
 * couleur seule. Un compteur facultatif (nombre de chantiers) s'affiche à droite.
 */
export function ElementNavigation({
  vers,
  icone,
  children,
  exact = false,
  compteur,
}: ElementNavigationProps) {
  return (
    <li>
      <NavLink
        to={vers}
        end={exact}
        className={({ isActive }) =>
          `${CLASSES_COMMUNES} ${isActive ? CLASSES_ACTIF : CLASSES_INACTIF}`
        }
      >
        <Icone nom={icone} />
        {children}
        {/* L'espace garde le nom accessible lisible (« Mes chantiers 4 ») ; il est invisible en flex. */}
        {compteur !== undefined && (
          <>
            {' '}
            <span className="ml-auto text-etiquette tabular-nums">{compteur}</span>
          </>
        )}
      </NavLink>
    </li>
  );
}
