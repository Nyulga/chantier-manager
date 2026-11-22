// Composant `Icone` du design system Balise : les pictogrammes de l'interface.

/** Pictogrammes disponibles : on en ajoute un en ajoutant une ligne à `TRACES`. */
export type NomIcone =
  'tableau-de-bord' | 'chantiers' | 'equipe' | 'invitation' | 'adresse' | 'plus' | 'valider';

type IconeProps = {
  readonly nom: NomIcone;
};

/** Tracés SVG sur une grille de 24 px, dessinés au trait (couleur du texte courant). */
const TRACES: Record<NomIcone, string> = {
  'tableau-de-bord': 'M3 3h7v9H3zM14 3h7v5h-7zM14 12h7v9h-7zM3 16h7v5H3z',
  chantiers: 'M3 21h18M5 21V7l7-4 7 4v14M9 21v-6h6v6',
  equipe:
    'M2 21c0-4 3-7 7-7s7 3 7 7M17 4a4 4 0 0 1 0 8M22 21c0-3-2-5.5-4.5-6.5M13 8a4 4 0 1 1-8 0 4 4 0 0 1 8 0',
  invitation: 'M5 5h14a2 2 0 0 1 2 2v10a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V7a2 2 0 0 1 2-2zM3 7l9 6 9-6',
  adresse:
    'M12 21s-7-6.5-7-12a7 7 0 0 1 14 0c0 5.5-7 12-7 12zM14.5 9a2.5 2.5 0 1 1-5 0 2.5 2.5 0 0 1 5 0',
  plus: 'M12 5v14M5 12h14',
  valider: 'm5 12 5 5 9-10',
};

/**
 * Pictogramme décoratif : il accompagne toujours un texte, il est donc caché des lecteurs
 * d'écran (`aria-hidden`). Il prend la couleur du texte et sa taille suit celle de la police.
 */
export function Icone({ nom }: IconeProps) {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
      className="size-5 shrink-0"
    >
      <path d={TRACES[nom]} />
    </svg>
  );
}
