// Ligne d'une étape : titre, statut et un bouton par action que l'API permet.
import { useState } from 'react';

import { Alerte, BadgeStatut, Bouton, Carte, Titre } from '@/ui';

import type { ActionEtape, Etape } from '../services/useEtapes';
import type { DemandeTransition } from '../services/useTransitionEtape';
import { FormulaireRefus } from './FormulaireRefus';

type LigneEtapeProps = {
  readonly etape: Etape;
  readonly enCours: boolean;
  /** Erreur de l'API pour cette étape, montrée dans sa carte (visible sans défiler sur mobile). */
  readonly erreur?: string | undefined;
  /** `apresSucces` est appelé quand l'API a accepté la demande. */
  readonly onAction: (
    demande: Omit<DemandeTransition, 'etapeId' | 'chantierId'>,
    apresSucces: () => void,
  ) => void;
};

const LIBELLES: Record<ActionEtape, string> = {
  demarrer: 'Démarrer',
  signaler_terminee: 'Signaler terminée',
  valider: 'Valider',
  refuser: 'Refuser',
};

/**
 * Seules les `actions_permises` de l'API ont un bouton : le frontend ne déduit aucun droit du
 * statut ni du profil. « Refuser » ouvre d'abord la saisie du commentaire.
 */
export function LigneEtape({ etape, enCours, erreur, onAction }: LigneEtapeProps) {
  const [refusOuvert, setRefusOuvert] = useState(false);
  // Le formulaire ne reste ouvert que tant que l'API permet de refuser : si l'étape a changé
  // entre-temps (autre utilisateur, 409), il disparaît au lieu d'offrir une action devenue interdite.
  const formulaireRefusVisible = refusOuvert && etape.actions_permises.includes('refuser');

  function choisir(action: ActionEtape): void {
    if (action === 'refuser') {
      setRefusOuvert(true);
      return;
    }
    onAction({ action }, () => undefined);
  }

  return (
    <Carte>
      <Titre niveau={3}>{etape.titre}</Titre>
      <BadgeStatut statut={etape.statut} />
      {etape.actions_permises.map((action) => (
        <Bouton
          key={action}
          variante={action === 'refuser' ? 'danger' : 'principal'}
          disabled={enCours}
          libelleAccessible={`${LIBELLES[action]} : ${etape.titre}`}
          onClick={() => {
            choisir(action);
          }}
        >
          {LIBELLES[action]}
        </Bouton>
      ))}
      {formulaireRefusVisible && (
        <FormulaireRefus
          enCours={enCours}
          erreur={erreur}
          onAnnuler={() => {
            setRefusOuvert(false);
          }}
          onConfirmer={(commentaire) => {
            onAction({ action: 'refuser', commentaire }, () => {
              setRefusOuvert(false);
            });
          }}
        />
      )}
      {erreur !== undefined && !formulaireRefusVisible && (
        <Alerte variante="erreur">{erreur}</Alerte>
      )}
    </Carte>
  );
}
