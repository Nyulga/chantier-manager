// Composant `Titre` du design system Balise : titres condensés de type « panneau de chantier ».
import type { ReactNode, Ref } from 'react';

/** Niveau de titre : 1 pour la page, 2 pour une section, 3 pour une carte. */
type NiveauTitre = 1 | 2 | 3;

type TitreProps = {
  readonly niveau: NiveauTitre;
  /**
   * Apparence, quand elle diffère du niveau : un titre de carte (taille 3) peut être de niveau 2
   * sur une page sans section, pour ne pas sauter de niveau dans le plan de la page.
   */
  readonly taille?: NiveauTitre;
  /**
   * Référence vers le titre. En la fournissant, on rend aussi le titre focalisable par programme
   * (hors de l'ordre de tabulation) : un écran peut y replacer le focus quand l'élément focalisé
   * disparaît, par exemple après la validation d'une étape.
   */
  readonly refTitre?: Ref<HTMLHeadingElement> | undefined;
  readonly children: ReactNode;
};

/*
 * Le niveau détermine l'élément HTML (la structure lue par les lecteurs d'écran), la taille
 * détermine l'apparence (échelle typographique de Balise, §3). Sur ordinateur, le titre de
 * page passe de 28 px à 44 px.
 */
const ELEMENT_PAR_NIVEAU = { 1: 'h1', 2: 'h2', 3: 'h3' } as const satisfies Record<
  NiveauTitre,
  'h1' | 'h2' | 'h3'
>;

const TAILLE_PAR_NIVEAU = {
  1: 'text-titre-page ordinateur:text-titre-page-ordinateur',
  2: 'text-titre-section',
  3: 'text-titre-carte',
} as const satisfies Record<NiveauTitre, string>;

/** Titre en Archivo condensé, majuscules, graisse 800 (utilitaire `titre-balise` du thème). */
export function Titre({ niveau, taille = niveau, refTitre, children }: TitreProps) {
  const Element = ELEMENT_PAR_NIVEAU[niveau];

  return (
    <Element
      ref={refTitre}
      tabIndex={refTitre === undefined ? undefined : -1}
      className={`titre-balise ${TAILLE_PAR_NIVEAU[taille]}`}
    >
      {children}
    </Element>
  );
}
