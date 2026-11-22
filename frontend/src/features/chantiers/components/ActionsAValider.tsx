// Actions d'une étape à valider : « Examiner » toujours, « Valider » seulement si l'API le permet.
import { Bouton, Icone, Lien } from '@/ui';

import type { EtapeAValider } from '../services/useEtapesAValider';

type ActionsAValiderProps = {
  readonly etape: EtapeAValider;
  readonly enCours: boolean;
  readonly onValider: (etape: EtapeAValider) => void;
};

/**
 * « Examiner » mène au chantier pour voir le détail avant de décider. « Valider » n'a de bouton
 * que si `actions_permises` contient `valider` : le frontend ne déduit aucun droit du profil.
 * Le nom accessible de chaque action reprend le titre de l'étape, car la liste en répète plusieurs.
 */
export function ActionsAValider({ etape, enCours, onValider }: ActionsAValiderProps) {
  return (
    <>
      <Lien
        vers={`/chantiers/${etape.chantier_id}`}
        variante="secondaire"
        libelleAccessible={`Examiner : ${etape.titre}`}
      >
        Examiner
      </Lien>
      {etape.actions_permises.includes('valider') && (
        <Bouton
          disabled={enCours}
          libelleAccessible={`Valider : ${etape.titre}`}
          onClick={() => {
            onValider(etape);
          }}
        >
          <Icone nom="valider" />
          Valider
        </Bouton>
      )}
    </>
  );
}
