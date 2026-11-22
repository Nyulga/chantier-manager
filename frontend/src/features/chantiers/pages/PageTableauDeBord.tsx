// Page « tableau de bord » (adresse `/`) : ce qui attend le chef, les chantiers et l'activité récente.
import { useState } from 'react';

import { Colonnes, Pile } from '@/ui';

import { EnTeteTableauDeBord } from '../components/EnTeteTableauDeBord';
import { SectionActivite } from '../components/SectionActivite';
import { SectionAValider } from '../components/SectionAValider';
import { SectionMesChantiers } from '../components/SectionMesChantiers';
import { useActiviteRecente } from '../services/useActiviteRecente';
import { useChantiers } from '../services/useChantiers';
import { estAccesRefuse, useEtapesAValider } from '../services/useEtapesAValider';
import { useProfilCourant } from '../services/useProfilCourant';
import { useValiderEtape } from '../services/useValiderEtape';

/**
 * Écran d'accueil. Il ne calcule rien : compteurs, avancement, retards et actions permises
 * viennent de l'API. La section « À valider » est demandée à l'API pour tous les profils : c'est
 * elle qui décide, et un 403 (ouvrier) masque la section sans message d'erreur.
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
      {!estAccesRefuse(aValider.error) && (
        <SectionAValider
          etapes={aValider.data}
          erreurChargement={aValider.error?.message}
          chantiers={chantiers.data}
          maintenant={maintenant}
          enCours={validation.isPending}
          erreurValidation={
            validation.isError
              ? { titre: validation.variables.titre, message: validation.error.message }
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
