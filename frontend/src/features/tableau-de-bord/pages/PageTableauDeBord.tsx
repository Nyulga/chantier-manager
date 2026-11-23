// Page « tableau de bord » (adresse `/`) : ce qui attend une décision, les chantiers et l'activité récente.
import { useState } from 'react';

import { Colonnes, Pile } from '@/ui';

import { EnTeteTableauDeBord } from '../components/EnTeteTableauDeBord';
import { SectionMesChantiers } from '../components/SectionMesChantiers';
import { useCapacites } from '../services/useCapacites';
import { useChantiers } from '../services/useChantiers';
import { ZoneActivite } from './ZoneActivite';
import { ZoneAValider } from './ZoneAValider';

/**
 * Écran d'accueil. Il ne calcule rien : compteurs, avancement, retards et actions permises
 * viennent de l'API. Les droits viennent de `/api/moi` : la section « À valider » et le lien de
 * création n'apparaissent que si elle les annonce.
 */
export function PageTableauDeBord() {
  const capacites = useCapacites();
  const chantiers = useChantiers();
  // La date est lue une seule fois : l'affichage ne change pas à chaque rendu.
  const [maintenant] = useState(() => new Date());

  return (
    <Pile espace="grand">
      <EnTeteTableauDeBord
        maintenant={maintenant}
        peutCreerChantier={capacites.data?.peut_creer_chantier === true}
      />
      <ZoneAValider
        autorisee={capacites.data?.peut_lister_etapes_a_valider === true}
        chantiers={chantiers.data}
        maintenant={maintenant}
      />
      <Colonnes
        laterale={
          <ZoneActivite
            chantiers={chantiers.data}
            role={capacites.data?.role}
            erreurRole={capacites.error?.message}
            maintenant={maintenant}
          />
        }
      >
        <SectionMesChantiers chantiers={chantiers.data} erreur={chantiers.error?.message} />
      </Colonnes>
    </Pile>
  );
}
