// Résumé d'un chantier pour l'aperçu du tableau de bord : la carte du design system, remplie avec les données de l'API.
import { CarteChantier, formaterDate, formaterDelai, PuceChantier } from '@/ui';

import type { Chantier } from '../services/useChantiers';

type ResumeChantierProps = {
  readonly chantier: Chantier;
};

/** Les puces d'état, ou rien quand le chantier n'a ni étape à valider ni retard. */
function PucesChantier({ chantier }: ResumeChantierProps) {
  return (
    <>
      {chantier.etapes_a_valider > 0 && (
        <PuceChantier variante="a-valider">{`${String(chantier.etapes_a_valider)} à valider`}</PuceChantier>
      )}
      {chantier.en_retard && <PuceChantier variante="en-retard">En retard</PuceChantier>}
    </>
  );
}

/**
 * Tout vient de l'API : avancement, compteurs d'étapes, retard et nombre de jours sont calculés
 * par le serveur (le frontend ne compare aucune date, il met en forme). Le titre est de niveau 3 :
 * l'aperçu est sous la section « Mes chantiers ».
 */
export function ResumeChantier({ chantier }: ResumeChantierProps) {
  const { adresse } = chantier;

  return (
    <CarteChantier
      nom={chantier.nom}
      vers={`/chantiers/${chantier.id}`}
      adresse={`${adresse.voie}, ${adresse.code_postal} ${adresse.ville}`}
      puces={<PucesChantier chantier={chantier} />}
      etapesValidees={chantier.etapes_validees}
      etapesTotal={chantier.etapes_total}
      pourcentage={chantier.avancement}
      echeance={formaterDate(chantier.echeance)}
      delai={formaterDelai({
        joursRestants: chantier.jours_restants,
        enRetard: chantier.en_retard,
      })}
      enRetard={chantier.en_retard}
    />
  );
}
