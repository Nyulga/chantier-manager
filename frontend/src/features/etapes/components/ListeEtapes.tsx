// Liste des étapes d'un chantier, ou le message qui dit qu'il n'y en a pas encore.
import { Texte } from '@/ui';

import type { Etape } from '../services/useEtapes';
import type { DemandeTransition } from '../services/useTransitionEtape';
import { LigneEtape } from './LigneEtape';

type ListeEtapesProps = {
  readonly etapes: readonly Etape[];
  readonly enCours: boolean;
  readonly onAction: (demande: DemandeTransition, apresSucces: () => void) => void;
};

/** Affiche les étapes dans l'ordre reçu de l'API ; chaque ligne montre ses actions permises. */
export function ListeEtapes({ etapes, enCours, onAction }: ListeEtapesProps) {
  if (etapes.length === 0) {
    return <Texte>Aucune étape pour le moment.</Texte>;
  }

  return etapes.map((etape) => (
    <LigneEtape
      key={etape.id}
      etape={etape}
      enCours={enCours}
      onAction={(demande, apresSucces) => {
        onAction({ etapeId: etape.id, ...demande }, apresSucces);
      }}
    />
  ));
}
