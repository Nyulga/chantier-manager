// Page « détail du chantier » (adresse `/chantiers/:id`) : informations, puis les étapes en dessous.
import { Outlet, useParams } from 'react-router';

import { Alerte, Lien, Pile, Texte, Titre } from '@/ui';

import { InformationsChantier } from '../components/InformationsChantier';
import { useChantier } from '../services/useChantier';

/**
 * Écran du chantier. Les étapes sont une page d'une autre fonctionnalité, affichée par `Outlet` :
 * une fonctionnalité ne peut pas en importer une autre (règle 05). On lui transmet ce qu'elle ne
 * peut pas connaître seule : l'identifiant, l'avancement et le droit d'ajouter une étape, tous
 * trois renvoyés par l'API. Son type est déclaré à l'identique dans `PageEtapesChantier`.
 */
export function PageDetailChantier() {
  const { id } = useParams();
  const chantier = useChantier(id ?? '');

  return (
    <Pile>
      <Lien vers="/chantiers">Retour aux chantiers</Lien>
      {chantier.isPending && <Texte variante="secondaire">Chargement du chantier…</Texte>}
      {chantier.isError && <Alerte variante="erreur">{chantier.error.message}</Alerte>}
      {chantier.data !== undefined && (
        <>
          <Titre niveau={1}>{chantier.data.nom}</Titre>
          <InformationsChantier chantier={chantier.data} />
          <Outlet
            context={{
              chantierId: chantier.data.id,
              avancement: chantier.data.avancement,
              peutAjouterEtape: chantier.data.peut_ajouter_etape,
            }}
          />
        </>
      )}
    </Pile>
  );
}
