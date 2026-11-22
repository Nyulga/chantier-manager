// Une ligne de la section « À valider » : l'étape, son chantier, son signalement et ses actions.
import type { Ref } from 'react';

import { formaterMoment, LigneAValider } from '@/ui';

import type { EtapeAValider } from '../services/useEtapesAValider';
import { ActionsAValider } from './ActionsAValider';

type LigneEtapeAValiderProps = {
  readonly etape: EtapeAValider;
  readonly nomChantier: string;
  readonly maintenant: Date;
  readonly enCours: boolean;
  readonly onValider: (etape: EtapeAValider) => void;
  /** Référence vers la ligne, pour y replacer le focus. */
  readonly reference: Ref<HTMLLIElement>;
};

/** Texte du signalement : l'API peut ne pas donner de date sur une donnée incohérente. */
function signalement(etape: EtapeAValider, maintenant: Date): string {
  return etape.signalee_le === null
    ? 'Signalée terminée'
    : `Signalée ${formaterMoment(etape.signalee_le, maintenant)}`;
}

/** Relie une étape à valider à la `LigneAValider` du design system. */
export function LigneEtapeAValider({
  etape,
  nomChantier,
  maintenant,
  enCours,
  onValider,
  reference,
}: LigneEtapeAValiderProps) {
  return (
    <LigneAValider
      ref={reference}
      titre={etape.titre}
      contexte={nomChantier}
      signalement={signalement(etape, maintenant)}
      actions={<ActionsAValider etape={etape} enCours={enCours} onValider={onValider} />}
    />
  );
}
