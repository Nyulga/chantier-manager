// Formulaire d'ajout d'une étape : un titre et un bouton.
import { useState } from 'react';

import { Bouton, Champ, Formulaire } from '@/ui';

type FormulaireAjoutEtapeProps = {
  readonly enCours: boolean;
  /** `apresSucces` est appelé quand l'API a accepté l'étape : le champ est alors vidé. */
  readonly onAjouter: (titre: string, apresSucces: () => void) => void;
};

/** Le titre est vérifié par l'API (422 si invalide) : le formulaire envoie ce qui est saisi. */
export function FormulaireAjoutEtape({ enCours, onAjouter }: FormulaireAjoutEtapeProps) {
  const [titre, setTitre] = useState('');

  return (
    <Formulaire
      onSubmit={() => {
        onAjouter(titre, () => {
          setTitre('');
        });
      }}
    >
      <Champ libelle="Titre de l’étape" valeur={titre} onChange={setTitre} requis />
      <Bouton type="submit" disabled={enCours}>
        Ajouter l’étape
      </Bouton>
    </Formulaire>
  );
}
