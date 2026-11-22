// Carte d'un chantier dans la liste : nom, ville, échéance, avancement et lien vers le détail.
import { BarreAvancement, Carte, formaterDate, Lien, Texte, Titre } from '@/ui';

import type { Chantier } from '../services/useChantiers';

type CarteChantierProps = {
  readonly chantier: Chantier;
};

/**
 * Résumé d'un chantier. L'avancement affiché est celui de l'API : la liste ne reçoit pas les
 * étapes, la barre n'affiche donc que le pourcentage.
 */
export function CarteChantier({ chantier }: CarteChantierProps) {
  return (
    <Carte>
      <Titre niveau={3}>{chantier.nom}</Titre>
      <Texte variante="secondaire">{chantier.adresse.ville}</Texte>
      <Texte variante="secondaire">{`Échéance : ${formaterDate(chantier.echeance)}`}</Texte>
      <BarreAvancement
        libelle={`Avancement de ${chantier.nom}`}
        pourcentage={chantier.avancement}
      />
      <Lien vers={`/chantiers/${chantier.id}`}>{`Ouvrir le chantier ${chantier.nom}`}</Lien>
    </Carte>
  );
}
