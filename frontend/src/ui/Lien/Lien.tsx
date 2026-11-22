// Composant `Lien` du design system Balise : un lien de navigation interne.
import type { ReactNode } from 'react';
import { Link } from 'react-router';

type LienProps = {
  readonly vers: string;
  readonly children: ReactNode;
};

/**
 * Lien vers une page de l'application, sans rechargement (enveloppe le `Link` de react-router).
 * Il est en `accent-ink` et souligné, jamais en jaune (règle d'or de Balise), et sa zone de
 * toucher fait au moins 44 px.
 */
export function Lien({ vers, children }: LienProps) {
  return (
    <Link
      to={vers}
      className="inline-flex min-h-cible items-center font-semibold text-accent-ink underline"
    >
      {children}
    </Link>
  );
}
