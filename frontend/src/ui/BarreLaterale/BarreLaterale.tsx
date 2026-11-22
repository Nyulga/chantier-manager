// Composant `BarreLaterale` du design system Balise : logo, navigation principale et pied de barre.
import type { ReactNode } from 'react';

type BarreLateraleProps = {
  /** Les éléments de navigation (`ElementNavigation` et `ElementNavigationBientot`). */
  readonly navigation: ReactNode;
  /** Le bas de la barre : ici le choix du profil. */
  readonly pied: ReactNode;
};

/**
 * Barre graphite (`fg`, avec le texte en `bg` : les deux s'inversent avec le thème sombre).
 *
 * Sur mobile (360 px), elle devient un en-tête empilé en haut de page : le logo, les entrées
 * de navigation sur une colonne (deux dès la tablette : la mention « Bientôt » ne tient pas
 * dans une demi-largeur de 360 px), puis le pied. Dès l'ordinateur, elle est une
 * colonne fixe de 248 px sur toute la hauteur de l'écran. Le logo porte les rayures
 * « balise » : c'est l'un des trois usages que Balise leur réserve (§4).
 */
export function BarreLaterale({ navigation, pied }: BarreLateraleProps) {
  return (
    <aside className="flex flex-col gap-5 bg-fg p-4 text-bg ordinateur:sticky ordinateur:top-0 ordinateur:h-screen ordinateur:w-barre-laterale ordinateur:shrink-0 ordinateur:gap-7 ordinateur:self-start ordinateur:overflow-y-auto ordinateur:px-4 ordinateur:py-6">
      <div className="flex flex-col gap-3 px-2">
        <div aria-hidden="true" className="rayures-balise h-2 w-10 rounded-controle" />
        <span className="titre-balise text-titre-section leading-none">Chantier Manager</span>
      </div>
      <nav aria-label="Navigation principale">
        <ul className="grid grid-cols-1 gap-1 tablette:grid-cols-2 ordinateur:flex ordinateur:flex-col">
          {navigation}
        </ul>
      </nav>
      <div className="flex flex-col gap-3 border-t border-muted px-2 pt-4 ordinateur:mt-auto">
        {pied}
      </div>
    </aside>
  );
}
