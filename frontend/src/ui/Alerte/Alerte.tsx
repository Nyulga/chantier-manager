// Composant `Alerte` du design system Balise : un message d'erreur.
import type { ReactNode } from 'react';

type AlerteProps = {
  readonly children: ReactNode;
};

/**
 * Message d'erreur encadré, annoncé tout de suite par les lecteurs d'écran (`role="alert"`). Le
 * titre « Erreur » écrit en toutes lettres et la bordure épaisse évitent que la couleur soit le
 * seul indice.
 */
export function Alerte({ children }: AlerteProps) {
  return (
    <div
      role="alert"
      className="flex flex-col gap-1 rounded-controle border-2 border-danger bg-danger-soft p-4 text-danger"
    >
      <strong className="text-etiquette uppercase">Erreur</strong>
      <span>{children}</span>
    </div>
  );
}
