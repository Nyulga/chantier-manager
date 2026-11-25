// Page des étapes d'un chantier : avancement, liste des étapes avec leurs actions, ajout d'étape.
import { Alerte, BarreAvancement, Pile, Texte, Titre } from '@/ui';

import { FormulaireAjoutEtape } from '../components/FormulaireAjoutEtape';
import { ListeEtapes } from '../components/ListeEtapes';
import { useAjouterEtape } from '../services/useAjouterEtape';
import { useAvancementChantier } from '../services/useAvancementChantier';
import { useEtapes } from '../services/useEtapes';
import { useIdChantier } from '../services/useIdChantier';
import { useTransitionEtape } from '../services/useTransitionEtape';

/**
 * Écran des étapes, affiché sous les informations du chantier. L'avancement et le droit d'ajouter
 * une étape sont ceux de l'API (le frontend ne compte pas les étapes validées) ; ils se mettent à
 * jour après chaque action, car les hooks invalident le chantier.
 */
export function PageEtapesChantier() {
  const chantierId = useIdChantier();
  const resume = useAvancementChantier(chantierId);
  const etapes = useEtapes(chantierId);
  const ajout = useAjouterEtape(chantierId);
  const transition = useTransitionEtape();

  const erreurTransition = transition.isError
    ? { etapeId: transition.variables.etapeId, erreur: transition.error }
    : undefined;

  return (
    <Pile>
      {resume.data !== undefined && (
        <BarreAvancement libelle="Avancement du chantier" pourcentage={resume.data.avancement} />
      )}
      <Titre niveau={2}>Étapes</Titre>
      {etapes.isPending && <Texte variante="secondaire">Chargement des étapes…</Texte>}
      {etapes.isError && <Alerte>{etapes.error.message}</Alerte>}
      {etapes.data !== undefined && (
        <ListeEtapes
          etapes={etapes.data}
          enCours={transition.isPending}
          erreur={erreurTransition}
          onAction={(demande, apresSucces) => {
            transition.mutate(demande, { onSuccess: apresSucces });
          }}
        />
      )}
      {resume.data?.peutAjouterEtape === true && (
        <FormulaireAjoutEtape
          enCours={ajout.isPending}
          erreur={ajout.error}
          onAjouter={(saisie, apresSucces) => {
            ajout.mutate(saisie, { onSuccess: apresSucces });
          }}
        />
      )}
    </Pile>
  );
}
