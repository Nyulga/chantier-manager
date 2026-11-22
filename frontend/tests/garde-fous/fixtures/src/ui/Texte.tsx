// Fixture conforme : un composant du design system, seul endroit où className est permis.
import type { ReactNode } from 'react';

export function Texte({ children }: { readonly children: ReactNode }) {
  return <p className="text-texte">{children}</p>;
}
