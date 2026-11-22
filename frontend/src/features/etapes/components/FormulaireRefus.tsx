// Formulaire de refus d'une étape : le commentaire du chef, puis la confirmation ou l'annulation.
import { useState } from 'react';

import { Bouton, Formulaire, ZoneTexte } from '@/ui';

type FormulaireRefusProps = {
  readonly onConfirmer: (commentaire: string) => void;
  readonly onAnnuler: () => void;
  readonly enCours: boolean;
  readonly erreur?: string | undefined;
};

/**
 * Le commentaire est obligatoire pour refuser, mais c'est l'API qui l'impose : elle répond 422 et
 * son message s'affiche sous le champ du motif, là où l'utilisateur regarde. Le frontend n'empêche pas l'envoi d'un commentaire vide.
 */
export function FormulaireRefus({ onConfirmer, onAnnuler, enCours, erreur }: FormulaireRefusProps) {
  const [commentaire, setCommentaire] = useState('');

  return (
    <Formulaire
      onSubmit={() => {
        onConfirmer(commentaire);
      }}
    >
      <ZoneTexte
        libelle="Motif du refus"
        valeur={commentaire}
        onChange={setCommentaire}
        erreur={erreur}
        requis
      />
      <Bouton type="submit" variante="danger" disabled={enCours}>
        Confirmer le refus
      </Bouton>
      <Bouton variante="secondaire" onClick={onAnnuler}>
        Annuler
      </Bouton>
    </Formulaire>
  );
}
