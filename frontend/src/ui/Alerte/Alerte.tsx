// Composant `Alerte` du design system Balise : un message d'erreur ou d'information.
import type { ReactNode } from 'react';

type VarianteAlerte = 'erreur' | 'information';

type AlerteProps = {
  readonly variante: VarianteAlerte;
  readonly children: ReactNode;
};

/*
 * Une erreur est annoncée tout de suite par les lecteurs d'écran (`role="alert"`) ; une
 * information l'est poliment (`role="status"`). Le titre écrit en toutes lettres et la bordure
 * plus épaisse de l'erreur évitent que la couleur soit le seul indice.
 */
const PRESENTATION_PAR_VARIANTE = {
  erreur: {
    role: 'alert',
    titre: 'Erreur',
    classes: 'border-2 border-danger bg-danger-soft text-danger',
  },
  information: {
    role: 'status',
    titre: 'Information',
    classes: 'border border-line bg-surface text-fg',
  },
} as const satisfies Record<VarianteAlerte, { role: string; titre: string; classes: string }>;

/** Message encadré, avec son titre (« Erreur » ou « Information ») suivi du texte. */
export function Alerte({ variante, children }: AlerteProps) {
  const { role, titre, classes } = PRESENTATION_PAR_VARIANTE[variante];

  return (
    <div role={role} className={`flex flex-col gap-1 rounded-controle p-4 ${classes}`}>
      <strong className="text-etiquette uppercase">{titre}</strong>
      <span>{children}</span>
    </div>
  );
}
