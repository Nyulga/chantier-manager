// Ligne d'une étape : titre, statut et un bouton par action que l'API permet.
import { useState } from 'react';

import { BadgeStatut, Bouton, Carte, Titre } from '@/ui';

import type { ActionEtape, Etape } from '../services/useEtapes';
import type { DemandeTransition } from '../services/useTransitionEtape';
import { FormulaireRefus } from './FormulaireRefus';

type LigneEtapeProps = {
  readonly etape: Etape;
  readonly enCours: boolean;
  /** `apresSucces` est appelé quand l'API a accepté la demande. */
  readonly onAction: (demande: Omit<DemandeTransition, 'etapeId'>, apresSucces: () => void) => void;
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
export function LigneEtape({ etape, enCours, onAction }: LigneEtapeProps) {
  const [refusOuvert, setRefusOuvert] = useState(false);

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
      {refusOuvert && (
        <FormulaireRefus
          enCours={enCours}
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
    </Carte>
  );
}
