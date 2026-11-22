// Composant `Titre` du design system Balise : titres condensés de type « panneau de chantier ».
import type { ReactNode } from 'react';

/** Niveau de titre : 1 pour la page, 2 pour une section, 3 pour une carte. */
type NiveauTitre = 1 | 2 | 3;

type TitreProps = {
  readonly niveau: NiveauTitre;
  readonly children: ReactNode;
};

/*
 * Le niveau détermine à la fois l'élément HTML (la structure lue par les lecteurs d'écran)
 * et la taille visuelle (échelle typographique de Balise, §3). Sur ordinateur, le titre de
 * page passe de 28 px à 44 px.
 */
const PRESENTATION_PAR_NIVEAU = {
  1: { Element: 'h1', taille: 'text-titre-page ordinateur:text-titre-page-ordinateur' },
  2: { Element: 'h2', taille: 'text-titre-section' },
  3: { Element: 'h3', taille: 'text-titre-carte' },
} as const satisfies Record<NiveauTitre, { Element: 'h1' | 'h2' | 'h3'; taille: string }>;

/** Titre en Archivo condensé, majuscules, graisse 800 (utilitaire `titre-balise` du thème). */
export function Titre({ niveau, children }: TitreProps) {
  const { Element, taille } = PRESENTATION_PAR_NIVEAU[niveau];

  return <Element className={`titre-balise ${taille}`}>{children}</Element>;
}
