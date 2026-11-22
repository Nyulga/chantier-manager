// Composant `ZoneTexte` du design system Balise : un champ de saisie sur plusieurs lignes.
import { useId } from 'react';

import {
  attributsErreur,
  CLASSES_CONTROLE,
  EnveloppeChamp,
} from '../EnveloppeChamp/EnveloppeChamp';

type ZoneTexteProps = {
  readonly libelle: string;
  readonly valeur: string;
  readonly onChange: (valeur: string) => void;
  readonly erreur?: string;
  readonly requis?: boolean;
};

/** Hauteur de départ de la zone, en lignes : assez pour un motif de refus sans défiler. */
const LIGNES_VISIBLES = 4;

/**
 * Zone de texte contrôlée, par exemple pour le commentaire obligatoire d'un refus.
 * Mêmes règles que `Champ` : libellé visible, erreur liée par `aria-describedby`.
 */
export function ZoneTexte({ libelle, valeur, onChange, erreur, requis }: ZoneTexteProps) {
  const identifiant = useId();

  return (
    <EnveloppeChamp identifiant={identifiant} libelle={libelle} erreur={erreur}>
      <textarea
        id={identifiant}
        rows={LIGNES_VISIBLES}
        value={valeur}
        required={requis}
        onChange={(evenement) => {
          onChange(evenement.target.value);
        }}
        className={`${CLASSES_CONTROLE} py-3`}
        {...attributsErreur(identifiant, erreur)}
      />
    </EnveloppeChamp>
  );
}
