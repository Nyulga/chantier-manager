// Page « liste des chantiers » (adresse `/chantiers`) : une carte par chantier visible par l'acteur.
import { Alerte, EntetePage, Lien, Pile, Texte } from '@/ui';

import { ListeChantiers } from '../components/ListeChantiers';
import { useChantiers } from '../services/useChantiers';
import { usePeutCreerChantier } from '../services/usePeutCreerChantier';

/**
 * Écran de la liste. Les chantiers affichés sont ceux que l'API renvoie ; le lien « Nouveau
 * chantier » n'apparaît que si elle annonce le droit d'en créer.
 */
export function PageListeChantiers() {
  const chantiers = useChantiers();
  const peutCreer = usePeutCreerChantier();

  return (
    <Pile espace="grand">
      <EntetePage titre="Chantiers">
        {peutCreer.data === true && (
          <Lien vers="/chantiers/nouveau" variante="principal">
            Nouveau chantier
          </Lien>
        )}
      </EntetePage>
      {chantiers.isPending && <Texte variante="secondaire">Chargement des chantiers…</Texte>}
      {chantiers.isError && <Alerte>{chantiers.error.message}</Alerte>}
      {chantiers.data !== undefined && <ListeChantiers chantiers={chantiers.data} />}
    </Pile>
  );
}
