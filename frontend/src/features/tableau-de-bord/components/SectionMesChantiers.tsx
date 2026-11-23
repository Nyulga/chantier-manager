// Section « Mes chantiers » du tableau de bord : les premières cartes et le lien vers la liste complète.
import { Alerte, Grille, Lien, Section, Texte } from '@/ui';

import type { Chantier } from '../services/useChantiers';
import { ResumeChantier } from './ResumeChantier';

type SectionMesChantiersProps = {
  /** `undefined` tant que la liste n'est pas chargée. */
  readonly chantiers: readonly Chantier[] | undefined;
  readonly erreur?: string | undefined;
};

/** Le tableau de bord n'affiche qu'un aperçu : la liste complète est sur `/chantiers`. */
const NOMBRE_CARTES_MAX = 4;

const TITRE = 'Mes chantiers';

/** « Voir les 6 chantiers », ou « Voir le chantier » quand il n'y en a qu'un. */
function libelleVoirTout(nombre: number): string {
  return nombre === 1 ? 'Voir le chantier' : `Voir les ${String(nombre)} chantiers`;
}

/**
 * Les chantiers affichés sont les premiers de l'API, dans son ordre. Le lien « Voir les N
 * chantiers » n'apparaît que s'il y en a : N est le nombre reçu, rien n'est calculé.
 */
export function SectionMesChantiers({ chantiers, erreur }: SectionMesChantiersProps) {
  if (erreur !== undefined) {
    return (
      <Section titre={TITRE}>
        <Alerte>{erreur}</Alerte>
      </Section>
    );
  }
  if (chantiers === undefined) {
    return (
      <Section titre={TITRE}>
        <Texte variante="secondaire">Chargement des chantiers…</Texte>
      </Section>
    );
  }
  if (chantiers.length === 0) {
    return (
      <Section titre={TITRE}>
        <Texte>Aucun chantier pour le moment.</Texte>
      </Section>
    );
  }

  return (
    <Section
      titre={TITRE}
      action={<Lien vers="/chantiers">{libelleVoirTout(chantiers.length)}</Lien>}
    >
      <Grille>
        {chantiers.slice(0, NOMBRE_CARTES_MAX).map((chantier) => (
          <ResumeChantier key={chantier.id} chantier={chantier} />
        ))}
      </Grille>
    </Section>
  );
}
