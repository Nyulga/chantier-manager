// Liste des chantiers de la page « Chantiers » : une carte par chantier, ou le message de liste vide.
import { Grille, ResumeChantier, Texte } from '@/ui';

import type { ChantierDeListe } from '../services/useChantiers';

type ListeChantiersProps = {
  readonly chantiers: readonly ChantierDeListe[];
};

/**
 * Affiche tous les chantiers reçus, dans l'ordre de l'API et sans limite. Le titre de carte est de
 * niveau 2 : la liste n'a pas de section, ses cartes suivent directement le titre de la page.
 */
export function ListeChantiers({ chantiers }: ListeChantiersProps) {
  if (chantiers.length === 0) {
    return <Texte>Aucun chantier pour le moment.</Texte>;
  }

  return (
    <Grille>
      {chantiers.map((chantier) => (
        <ResumeChantier
          key={chantier.id}
          {...chantier}
          vers={`/chantiers/${chantier.id}`}
          niveauTitre={2}
        />
      ))}
    </Grille>
  );
}
