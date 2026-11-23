// Formulaire de refus d'une étape : le commentaire du chef, puis la confirmation ou l'annulation.
import { useState } from 'react';

import { Alerte, Bouton, Formulaire, ZoneTexte } from '@/ui';

import type { ErreurApi } from '../services/useTransitionEtape';

type FormulaireRefusProps = {
  readonly onConfirmer: (commentaire: string) => void;
  readonly onAnnuler: () => void;
  readonly enCours: boolean;
  /** Erreur de l'API : son message sur le commentaire s'affiche sous le champ, les autres dans une alerte. */
  readonly erreur?: ErreurApi | undefined;
};

/** Nom du champ dans le corps de la requête, tel que l'API le désigne dans ses erreurs. */
const CHAMP_COMMENTAIRE = 'commentaire';

/**
 * Le commentaire est obligatoire pour refuser, mais c'est l'API qui l'impose : elle répond 422 et
 * son message s'affiche sous le champ du motif, là où l'utilisateur regarde, et il est annoncé aux
 * lecteurs d'écran. Le frontend n'empêche pas l'envoi d'un commentaire vide.
 */
export function FormulaireRefus({ onConfirmer, onAnnuler, enCours, erreur }: FormulaireRefusProps) {
  const [commentaire, setCommentaire] = useState('');
  const messageGlobal = erreur?.messageGlobal([CHAMP_COMMENTAIRE]);

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
        erreur={erreur?.messageDuChamp(CHAMP_COMMENTAIRE)}
        requis
      />
      {messageGlobal !== undefined && <Alerte>{messageGlobal}</Alerte>}
      <Bouton type="submit" variante="danger" disabled={enCours}>
        Confirmer le refus
      </Bouton>
      <Bouton variante="secondaire" onClick={onAnnuler}>
        Annuler
      </Bouton>
    </Formulaire>
  );
}
