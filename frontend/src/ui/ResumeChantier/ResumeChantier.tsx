// Composant `ResumeChantier` du design system Balise : la carte de résumé d'un chantier, remplie de valeurs simples.
import { CarteChantier } from '../CarteChantier/CarteChantier';
import { formaterDate } from '../format/formaterDate';
import { formaterDelai } from '../format/formaterDelai';
import { PuceChantier } from '../PuceChantier/PuceChantier';

type ResumeChantierProps = {
  readonly nom: string;
  /** Adresse de la page du chantier. */
  readonly vers: string;
  /** Adresse postale déjà mise à plat (« 12 rue des Lilas, 69003 Lyon »). */
  readonly adresse: string;
  readonly etapesValidees: number;
  readonly etapesTotal: number;
  /** Avancement en pourcentage, déjà calculé par l'API. */
  readonly avancement: number;
  /** Nombre d'étapes qui attendent une décision : la puce n'apparaît qu'au-dessus de zéro. */
  readonly etapesAValider: number;
  /** Échéance au format ISO (`AAAA-MM-JJ`), écrite ici en `JJ/MM/AAAA`. */
  readonly echeance: string;
  /** Jours restants, ou jours de retard quand `enRetard` : l'API les a déjà comptés. */
  readonly joursRestants: number;
  readonly enRetard: boolean;
  /** Niveau du titre : 3 sous une section de page (par défaut), 2 quand la page n'a pas de section. */
  readonly niveauTitre?: 2 | 3 | undefined;
};

/** Les puces d'état, ou rien quand le chantier n'a ni étape à valider ni retard. */
function PucesChantier({
  etapesAValider,
  enRetard,
}: Pick<ResumeChantierProps, 'etapesAValider' | 'enRetard'>) {
  return (
    <>
      {etapesAValider > 0 && (
        <PuceChantier variante="a-valider">{`${String(etapesAValider)} à valider`}</PuceChantier>
      )}
      {enRetard && <PuceChantier variante="en-retard">En retard</PuceChantier>}
    </>
  );
}

/**
 * Carte de résumé d'un chantier, la même sur la liste des chantiers et sur le tableau de bord.
 * Tout vient de l'API : avancement, compteurs, retard et nombre de jours sont calculés par le
 * serveur (le frontend ne compare aucune date, il met en forme).
 */
export function ResumeChantier({
  nom,
  vers,
  adresse,
  etapesValidees,
  etapesTotal,
  avancement,
  etapesAValider,
  echeance,
  joursRestants,
  enRetard,
  niveauTitre,
}: ResumeChantierProps) {
  return (
    <CarteChantier
      nom={nom}
      vers={vers}
      adresse={adresse}
      puces={<PucesChantier etapesAValider={etapesAValider} enRetard={enRetard} />}
      etapesValidees={etapesValidees}
      etapesTotal={etapesTotal}
      pourcentage={avancement}
      echeance={formaterDate(echeance)}
      delai={formaterDelai({ joursRestants, enRetard })}
      enRetard={enRetard}
      niveauTitre={niveauTitre}
    />
  );
}
