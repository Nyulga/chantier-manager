// Résumé d'un chantier : la carte du design system, remplie avec les données de l'API.
import { CarteChantier, formaterDate, formaterDelai, PuceChantier } from '@/ui';

import type { Chantier } from '../services/useChantiers';

type ResumeChantierProps = {
  readonly chantier: Chantier;
  /** Niveau du titre : 3 sous une section de page (par défaut), 2 sur une page sans section. */
  readonly niveauTitre?: 2 | 3 | undefined;
};

/** Les puces d'état, ou rien quand le chantier n'a ni étape à valider ni retard. */
function PucesChantier({ chantier }: { readonly chantier: Chantier }) {
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
 * par le serveur (le frontend ne compare aucune date, il met en forme).
 */
export function ResumeChantier({ chantier, niveauTitre }: ResumeChantierProps) {
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
      niveauTitre={niveauTitre}
    />
  );
}
