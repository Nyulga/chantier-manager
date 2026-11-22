// Section « Activité récente » du tableau de bord : les derniers changements de statut des étapes.
import { Alerte, FilActivite, formaterMoment, Section, Texte } from '@/ui';

import type { EntreeActivite } from '../services/useActiviteRecente';
import type { Chantier } from '../services/useChantiers';
import { libelleActivite } from './libelleActivite';
import { nomDuChantier } from './nomDuChantier';

type SectionActiviteProps = {
  /** `undefined` tant que le fil n'est pas chargé. */
  readonly entrees: readonly EntreeActivite[] | undefined;
  readonly erreur?: string | undefined;
  readonly chantiers: readonly Chantier[] | undefined;
  /** Rôle de l'utilisateur courant : ses propres actions s'écrivent « Tu as… ». */
  readonly profil: EntreeActivite['role'];
  readonly maintenant: Date;
};

const TITRE = 'Activité récente';

/** L'API ne donne pas d'identifiant d'entrée : l'étape et la date suffisent à distinguer deux entrées. */
function identifiant(entree: EntreeActivite): string {
  return `${entree.etape_id}-${entree.date}`;
}

/**
 * Chaque entrée devient « qui + quoi », puis « chantier · quand ». Le fil garde l'ordre de
 * l'API (du plus récent au plus ancien) ; le nom du chantier vient de la liste déjà chargée.
 */
export function SectionActivite({
  entrees,
  erreur,
  chantiers,
  profil,
  maintenant,
}: SectionActiviteProps) {
  if (erreur !== undefined) {
    return (
      <Section titre={TITRE}>
        <Alerte variante="erreur">{erreur}</Alerte>
      </Section>
    );
  }
  if (entrees === undefined) {
    return (
      <Section titre={TITRE}>
        <Texte variante="secondaire">Chargement de l’activité…</Texte>
      </Section>
    );
  }
  if (entrees.length === 0) {
    return (
      <Section titre={TITRE}>
        <Texte>Aucune activité pour le moment.</Texte>
      </Section>
    );
  }

  return (
    <Section titre={TITRE}>
      <FilActivite
        libelle={TITRE}
        entrees={entrees.map((entree) => ({
          id: identifiant(entree),
          ...libelleActivite(entree, profil),
          contexte: `${nomDuChantier(chantiers, entree.chantier_id)} · ${formaterMoment(entree.date, maintenant)}`,
        }))}
      />
    </Section>
  );
}
