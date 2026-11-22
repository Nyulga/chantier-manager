// Page des étapes d'un chantier : avancement, liste des étapes avec leurs actions, ajout d'étape.
import { useOutletContext } from 'react-router';

import { Alerte, BarreAvancement, Pile, Texte, Titre } from '@/ui';

import { FormulaireAjoutEtape } from '../components/FormulaireAjoutEtape';
import { ListeEtapes } from '../components/ListeEtapes';
import { useAjouterEtape } from '../services/useAjouterEtape';
import { useEtapes } from '../services/useEtapes';
import { useTransitionEtape } from '../services/useTransitionEtape';

/**
 * Ce que la page du chantier transmet par `Outlet` (déclaré à l'identique dans
 * `PageDetailChantier`) : tout vient de l'API, rien n'est calculé ici.
 */
type ContexteEtapes = {
  readonly chantierId: string;
  readonly avancement: number;
  readonly peutAjouterEtape: boolean;
};

/**
 * Écran des étapes, affiché sous les informations du chantier. L'avancement est celui de l'API
 * (le frontend ne compte pas les étapes validées) ; il se met à jour après chaque action, car
 * les hooks invalident le chantier.
 */
export function PageEtapesChantier() {
  const { chantierId, avancement, peutAjouterEtape } = useOutletContext<ContexteEtapes>();
  const etapes = useEtapes(chantierId);
  const ajout = useAjouterEtape(chantierId);
  const transition = useTransitionEtape();

  return (
    <Pile>
      <BarreAvancement libelle="Avancement du chantier" pourcentage={avancement} />
      <Titre niveau={2}>Étapes</Titre>
      {etapes.isPending && <Texte variante="secondaire">Chargement des étapes…</Texte>}
      {etapes.isError && <Alerte variante="erreur">{etapes.error.message}</Alerte>}
      {transition.isError && <Alerte variante="erreur">{transition.error.message}</Alerte>}
      {etapes.data !== undefined && (
        <ListeEtapes
          etapes={etapes.data}
          enCours={transition.isPending}
          onAction={(demande, apresSucces) => {
            transition.mutate(demande, { onSuccess: apresSucces });
          }}
        />
      )}
      {ajout.isError && <Alerte variante="erreur">{ajout.error.message}</Alerte>}
      {peutAjouterEtape && (
        <FormulaireAjoutEtape
          enCours={ajout.isPending}
          onAjouter={(titre, apresSucces) => {
            ajout.mutate(titre, { onSuccess: apresSucces });
          }}
        />
      )}
    </Pile>
  );
}
