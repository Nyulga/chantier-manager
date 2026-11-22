// Composant `Champ` du design system Balise : un champ de saisie sur une ligne.
import { useId } from 'react';

import {
  attributsErreur,
  CLASSES_CONTROLE,
  EnveloppeChamp,
} from '../EnveloppeChamp/EnveloppeChamp';

type TypeChamp = 'text' | 'date' | 'number';

type ChampProps = {
  readonly libelle: string;
  readonly valeur: string;
  readonly onChange: (valeur: string) => void;
  readonly type?: TypeChamp;
  readonly erreur?: string | undefined;
  readonly requis?: boolean;
};

/**
 * Champ contrôlé : le parent garde la valeur (texte, même pour `number` et `date`) et reçoit
 * chaque saisie. Le libellé est visible et associé au champ ; l'erreur, fournie par l'API ou
 * par la saisie, est liée par `aria-describedby`.
 */
export function Champ({ libelle, valeur, onChange, type = 'text', erreur, requis }: ChampProps) {
  const identifiant = useId();

  return (
    <EnveloppeChamp identifiant={identifiant} libelle={libelle} erreur={erreur}>
      <input
        id={identifiant}
        type={type}
        value={valeur}
        required={requis}
        onChange={(evenement) => {
          onChange(evenement.target.value);
        }}
        className={`${CLASSES_CONTROLE} min-h-cible-mobile ordinateur:min-h-cible`}
        {...attributsErreur(identifiant, erreur)}
      />
    </EnveloppeChamp>
  );
}
