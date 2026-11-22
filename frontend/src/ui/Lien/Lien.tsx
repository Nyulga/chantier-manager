// Composant `Lien` du design system Balise : un lien de navigation interne.
import type { ReactNode } from 'react';
import { Link } from 'react-router';

import { classesBouton } from '../Bouton/classesBouton';

/**
 * Apparence du lien : `texte` (par défaut) ou celle d'un bouton `principal` ou `secondaire`,
 * pour une action qui change de page (« Nouveau chantier », « Examiner »).
 */
type VarianteLien = 'texte' | 'principal' | 'secondaire';

type LienProps = {
  readonly vers: string;
  readonly children: ReactNode;
  readonly variante?: VarianteLien;
  /** Nom lu par les lecteurs d'écran quand plusieurs liens portent le même libellé visible. */
  readonly libelleAccessible?: string;
};

/** Un lien de texte est en `accent-ink` et souligné, jamais en jaune (règle d'or de Balise). */
const CLASSES_TEXTE =
  'inline-flex min-h-cible items-center font-semibold text-accent-ink underline';

/**
 * Lien vers une page de l'application, sans rechargement (enveloppe le `Link` de react-router).
 * Sa zone de toucher fait au moins 44 px ; sous l'apparence d'un bouton, il en reprend les
 * dimensions (52 à 56 px sur mobile) mais reste un lien pour les lecteurs d'écran.
 */
export function Lien({ vers, children, variante = 'texte', libelleAccessible }: LienProps) {
  return (
    <Link
      to={vers}
      aria-label={libelleAccessible}
      className={variante === 'texte' ? CLASSES_TEXTE : classesBouton(variante)}
    >
      {children}
    </Link>
  );
}
