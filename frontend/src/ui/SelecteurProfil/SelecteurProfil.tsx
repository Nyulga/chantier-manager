// Composant `SelecteurProfil` du design system Balise : le choix du profil, Chef ou Ouvrier.
import { useId } from 'react';

type ProfilSelectionnable = 'chef' | 'ouvrier';

type SelecteurProfilProps = {
  readonly valeur: ProfilSelectionnable;
  readonly onChange: (profil: ProfilSelectionnable) => void;
};

const OPTIONS: readonly { readonly valeur: ProfilSelectionnable; readonly libelle: string }[] = [
  { valeur: 'chef', libelle: 'Chef' },
  { valeur: 'ouvrier', libelle: 'Ouvrier' },
];

/**
 * Choix du profil de l'utilisateur, tant qu'il n'y a pas d'authentification (phase squelette).
 *
 * Des boutons radio natifs : le clavier et les lecteurs d'écran les comprennent sans code en plus.
 * Le composant est contrôlé : la valeur et le changement viennent de ses props.
 *
 * Il ne fixe aucune couleur : le texte et la pastille des boutons radio (`accent-current`)
 * reprennent celle du conteneur, car on le pose aussi sur la barre latérale graphite, où un
 * texte `fg` serait invisible.
 */
export function SelecteurProfil({ valeur, onChange }: SelecteurProfilProps) {
  // Identifiant unique : plusieurs sélecteurs peuvent coexister sans se disputer la légende.
  const identifiantLegende = useId();

  return (
    <fieldset
      role="radiogroup"
      aria-labelledby={identifiantLegende}
      className="flex flex-col gap-2"
    >
      <legend id={identifiantLegende} className="text-secondaire font-semibold">
        Profil
      </legend>
      <div className="flex gap-4">
        {OPTIONS.map((option) => (
          <label
            key={option.valeur}
            className="flex min-h-cible-mobile items-center gap-2 text-texte ordinateur:min-h-cible"
          >
            <input
              type="radio"
              name={identifiantLegende}
              value={option.valeur}
              checked={valeur === option.valeur}
              onChange={() => {
                onChange(option.valeur);
              }}
              className="accent-current"
            />
            {option.libelle}
          </label>
        ))}
      </div>
    </fieldset>
  );
}
