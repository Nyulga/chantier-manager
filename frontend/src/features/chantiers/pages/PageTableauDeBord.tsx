// Page « tableau de bord » (adresse `/`) : ce qui attend le chef, les chantiers et l'activité récente.
import { useState } from 'react';

import { Colonnes, Pile } from '@/ui';

import { EnTeteTableauDeBord } from '../components/EnTeteTableauDeBord';
import { SectionActivite } from '../components/SectionActivite';
import { SectionAValider } from '../components/SectionAValider';
import { SectionMesChantiers } from '../components/SectionMesChantiers';
import { useActiviteRecente } from '../services/useActiviteRecente';
import { useChantiers } from '../services/useChantiers';
import { useEtapesAValider } from '../services/useEtapesAValider';
import { useProfilCourant } from '../services/useProfilCourant';
import { useValiderEtape } from '../services/useValiderEtape';

/**
 * Écran d'accueil. Il ne calcule rien : compteurs, avancement, retards et actions permises
 * viennent de l'API. La section « À valider » n'existe que pour le chef (l'API répond 403 à un
 * ouvrier, et le hook ne l'interroge pas).
 */
export function PageTableauDeBord() {
  const profil = useProfilCourant();
  const chantiers = useChantiers();
  const aValider = useEtapesAValider();
  const activite = useActiviteRecente();
  const validation = useValiderEtape();
  // La date est lue une seule fois : l'affichage ne change pas à chaque rendu.
  const [maintenant] = useState(() => new Date());

  return (
    <Pile espace="grand">
      <EnTeteTableauDeBord maintenant={maintenant} peutCreerChantier={profil === 'chef'} />
      {profil === 'chef' && (
        <SectionAValider
          etapes={aValider.data}
          erreurChargement={aValider.error?.message}
          chantiers={chantiers.data}
          maintenant={maintenant}
          enCours={validation.isPending}
          erreurValidation={
            validation.isError
              ? { etapeId: validation.variables.id, message: validation.error.message }
              : undefined
          }
          onValider={(etape) => {
            validation.mutate(etape);
          }}
        />
      )}
      <Colonnes
        laterale={
          <SectionActivite
            entrees={activite.data}
            erreur={activite.error?.message}
            chantiers={chantiers.data}
            profil={profil}
            maintenant={maintenant}
          />
        }
      >
        <SectionMesChantiers chantiers={chantiers.data} erreur={chantiers.error?.message} />
      </Colonnes>
    </Pile>
  );
}
