// Liste des étapes d'un chantier, ou le message qui dit qu'il n'y en a pas encore.
import { Texte } from '@/ui';

import type { Etape } from '../services/useEtapes';
import type { DemandeTransitionEtape, ErreurApi } from '../services/useTransitionEtape';
import { LigneEtape } from './LigneEtape';

type ListeEtapesProps = {
  readonly etapes: readonly Etape[];
  readonly enCours: boolean;
  /** Erreur de la dernière demande, avec l'étape concernée : seule sa carte l'affiche. */
  readonly erreur?: { readonly etapeId: string; readonly erreur: ErreurApi } | undefined;
  readonly onAction: (demande: DemandeTransitionEtape, apresSucces: () => void) => void;
};

/** Affiche les étapes dans l'ordre reçu de l'API ; chaque ligne montre ses actions permises. */
export function ListeEtapes({ etapes, enCours, erreur, onAction }: ListeEtapesProps) {
  if (etapes.length === 0) {
    return <Texte>Aucune étape pour le moment.</Texte>;
  }

  return etapes.map((etape) => (
    <LigneEtape
      key={etape.id}
      etape={etape}
      enCours={enCours}
      erreur={erreur?.etapeId === etape.id ? erreur.erreur : undefined}
      onAction={(demande, apresSucces) => {
        // La version affichée part avec la demande : l'API refuse (409) si l'étape a changé depuis.
        onAction(
          { etapeId: etape.id, chantierId: etape.chantier_id, version: etape.version, ...demande },
          apresSucces,
        );
      }}
    />
  ));
}
