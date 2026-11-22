// Structure commune des champs de saisie Balise : libellé visible, contrôle, message d'erreur.
// Interne au design system : seuls `Champ` et `ZoneTexte` l'utilisent, il n'est pas exporté.
import type { ReactNode } from 'react';

type EnveloppeChampProps = {
  readonly identifiant: string;
  readonly libelle: string;
  readonly erreur: string | undefined;
  readonly children: ReactNode;
};

/**
 * Classes communes aux contrôles de saisie (Balise §5) : hauteur de 52 px sur mobile et 44 px
 * sur ordinateur, bordure `line`, et bordure de 2 px `fg` au focus.
 */
export const CLASSES_CONTROLE =
  'w-full rounded-controle border border-line bg-surface px-3 text-texte text-fg ' +
  'focus:border-2 focus:border-fg aria-invalid:border-danger';

/** Identifiant du message d'erreur, partagé avec `aria-describedby` du contrôle. */
export function identifiantErreur(identifiant: string): string {
  return `${identifiant}-erreur`;
}

/**
 * Attributs d'accessibilité du contrôle : il est invalide et décrit par l'erreur quand il y en a une.
 * Le message, écrit en toutes lettres, évite que la couleur soit le seul indice.
 */
export function attributsErreur(identifiant: string, erreur: string | undefined) {
  if (erreur === undefined) {
    return {};
  }
  return { 'aria-invalid': true, 'aria-describedby': identifiantErreur(identifiant) } as const;
}

/** Libellé toujours visible au-dessus du contrôle ; l'erreur s'affiche en dessous, en `danger`. */
export function EnveloppeChamp({ identifiant, libelle, erreur, children }: EnveloppeChampProps) {
  return (
    <div className="flex flex-col gap-1">
      <label htmlFor={identifiant} className="text-secondaire font-semibold text-fg">
        {libelle}
      </label>
      {children}
      {erreur !== undefined && (
        <p id={identifiantErreur(identifiant)} className="text-secondaire text-danger">
          {erreur}
        </p>
      )}
    </div>
  );
}
