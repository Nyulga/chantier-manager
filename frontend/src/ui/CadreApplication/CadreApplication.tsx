// Composant `CadreApplication` du design system Balise : la mise en page de tous les écrans.
import type { ReactNode } from 'react';

type CadreApplicationProps = {
  /** La barre latérale (`BarreLaterale`), placée avant le contenu pour le clavier et les lecteurs d'écran. */
  readonly barreLaterale: ReactNode;
  readonly children: ReactNode;
};

/**
 * Barre latérale puis zone principale. Sur mobile elles s'empilent (la barre devient un
 * en-tête), dès l'ordinateur elles se placent côte à côte. Le cadre porte le seul `<main>` de
 * l'écran : c'est le repère que les lecteurs d'écran proposent pour sauter la navigation.
 * `min-w-0` laisse la zone principale rétrécir plutôt que de provoquer un défilement horizontal.
 */
export function CadreApplication({ barreLaterale, children }: CadreApplicationProps) {
  return (
    <div className="flex min-h-screen flex-col ordinateur:flex-row">
      {barreLaterale}
      <main className="mx-auto flex w-full min-w-0 max-w-contenu flex-1 flex-col gap-7 p-4 tablette:p-8 ordinateur:px-10 ordinateur:pb-10">
        {children}
      </main>
    </div>
  );
}
