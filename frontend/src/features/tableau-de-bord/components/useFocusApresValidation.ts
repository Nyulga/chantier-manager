// Gestion du focus de la section « À valider » : le replacer quand la ligne validée disparaît.
import { useEffect, useRef, type RefCallback, type RefObject } from 'react';

import type { EtapeAValider } from '../services/useEtapesAValider';

/** Ce que le composant doit brancher sur ses éléments, et l'appel à faire avant d'envoyer la validation. */
type FocusApresValidation = {
  /** À poser sur le titre de la section : repli quand il ne reste aucune étape suivante. */
  readonly refTitre: RefObject<HTMLHeadingElement | null>;
  /** À poser sur la ligne de l'étape `id`. */
  readonly refLigne: (id: string) => RefCallback<HTMLLIElement>;
  /** À appeler quand l'utilisateur lance la validation de l'étape `id`. */
  readonly memoriser: (id: string) => void;
};

/**
 * Après « Valider », le bouton cliqué est désactivé puis sa ligne disparaît de la liste : le
 * navigateur laisse alors le focus sur `<body>`, et un utilisateur au clavier ou au lecteur
 * d'écran repart du haut de la page (WCAG 2.4.3, ordre du focus). On le replace donc, une fois la
 * demande terminée (réussie ou non), sur la ligne qui suivait l'étape, ou à défaut sur le titre
 * de la section, qui est aussi près de l'erreur éventuelle.
 */
export function useFocusApresValidation(
  etapes: readonly EtapeAValider[] | undefined,
  enCours: boolean,
): FocusApresValidation {
  const refTitre = useRef<HTMLHeadingElement>(null);
  const lignes = useRef(new Map<string, HTMLLIElement>());
  // `null` : aucune validation en attente ; sinon l'identifiant de la ligne qui suivait (ou `undefined`).
  const suivante = useRef<{ readonly id: string | undefined } | null>(null);

  useEffect(() => {
    if (enCours || suivante.current === null) {
      return;
    }
    const { id } = suivante.current;
    suivante.current = null;
    const ligne = id === undefined ? undefined : lignes.current.get(id);
    (ligne ?? refTitre.current)?.focus();
  }, [enCours, etapes]);

  return {
    refTitre,
    refLigne: (id) => (element) => {
      if (element !== null) {
        lignes.current.set(id, element);
      }
      return () => {
        lignes.current.delete(id);
      };
    },
    memoriser: (id) => {
      const position = etapes?.findIndex((etape) => etape.id === id) ?? -1;
      suivante.current = { id: etapes?.[position + 1]?.id };
    },
  };
}
