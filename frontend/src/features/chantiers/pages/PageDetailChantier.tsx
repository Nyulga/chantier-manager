// Page « détail du chantier » (adresse `/chantiers/:id`) : informations, puis les étapes en dessous.
import { Outlet } from 'react-router';

import { Alerte, Lien, PageIntrouvable, Pile, Texte, Titre } from '@/ui';

import { InformationsChantier } from '../components/InformationsChantier';
import { useChantier } from '../services/useChantier';
import { useIdChantier } from '../services/useIdChantier';

/**
 * Écran du chantier. Les étapes sont une page d'une autre fonctionnalité, affichée par `Outlet` :
 * une fonctionnalité ne peut pas en importer une autre (règle 05). Elle lit elle-même ce qu'il
 * lui faut dans l'API (voir `useAvancementChantier`) : rien n'est transmis d'une page à l'autre.
 *
 * Un chantier que l'API ne connaît pas (404, y compris un identifiant mal formé) donne la page
 * introuvable, comme une adresse inconnue.
 */
export function PageDetailChantier() {
  const chantier = useChantier(useIdChantier());

  if (chantier.error?.introuvable === true) {
    return <PageIntrouvable />;
  }

  return (
    <Pile>
      <Lien vers="/chantiers">Retour aux chantiers</Lien>
      {chantier.isPending && <Texte variante="secondaire">Chargement du chantier…</Texte>}
      {chantier.isError && <Alerte>{chantier.error.message}</Alerte>}
      {chantier.data !== undefined && (
        <>
          <Titre niveau={1}>{chantier.data.nom}</Titre>
          <InformationsChantier chantier={chantier.data} />
          <Outlet />
        </>
      )}
    </Pile>
  );
}
