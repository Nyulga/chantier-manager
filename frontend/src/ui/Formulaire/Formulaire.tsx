// Composant `Formulaire` du design system Balise : regroupe des champs et un bouton d'envoi.
import type { ReactNode } from 'react';

type FormulaireProps = {
  readonly children: ReactNode;
  readonly onSubmit: () => void;
};

/**
 * Formulaire qui s'envoie sans recharger la page.
 *
 * `noValidate` coupe les bulles de validation du navigateur, en anglais ou mal placées : la
 * saisie est vérifiée par l'API, dont les erreurs s'affichent sous les champs concernés.
 */
export function Formulaire({ children, onSubmit }: FormulaireProps) {
  return (
    <form
      noValidate
      onSubmit={(evenement) => {
        evenement.preventDefault();
        onSubmit();
      }}
      className="flex flex-col gap-4"
    >
      {children}
    </form>
  );
}
