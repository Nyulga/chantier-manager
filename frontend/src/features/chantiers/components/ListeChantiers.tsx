// Liste des chantiers de la page « Chantiers » : une carte par chantier, ou le message de liste vide.
import { Grille, Texte } from '@/ui';

import type { Chantier } from '../services/useChantiers';
import { ResumeChantier } from './ResumeChantier';

type ListeChantiersProps = {
  readonly chantiers: readonly Chantier[];
};

/** Affiche tous les chantiers reçus, dans l'ordre de l'API et sans limite. */
export function ListeChantiers({ chantiers }: ListeChantiersProps) {
  if (chantiers.length === 0) {
    return <Texte>Aucun chantier pour le moment.</Texte>;
  }

  return (
    <Grille>
      {chantiers.map((chantier) => (
        <ResumeChantier key={chantier.id} chantier={chantier} />
      ))}
    </Grille>
  );
}
