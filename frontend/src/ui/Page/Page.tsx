// Composant `Page` du design system Balise : la zone principale d'un écran.
import type { ReactNode } from 'react';

type PageProps = {
  readonly children: ReactNode;
};

/**
 * Zone principale d'un écran (`<main>`), centrée et bornée en largeur.
 *
 * Il n'y en a qu'une par écran : c'est le point de repère que les lecteurs d'écran proposent
 * pour sauter la navigation. Les marges sont de 16 px sur mobile, puis de 32 px dès la tablette
 * (conception d'abord pour le mobile).
 */
export function Page({ children }: PageProps) {
  return (
    <main className="mx-auto flex min-h-screen w-full max-w-4xl flex-col gap-6 p-4 tablette:p-8">
      {children}
    </main>
  );
}
