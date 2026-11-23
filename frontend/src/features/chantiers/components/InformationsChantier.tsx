// Informations d'un chantier sur sa page de détail : adresse, client, dates et budget.
import { Carte, formaterDate, formaterMontant, Texte } from '@/ui';

import type { Chantier } from '../services/useChantier';

type InformationsChantierProps = {
  readonly chantier: Chantier;
};

/**
 * Le budget n'est affiché que si l'API le renvoie : elle le met à `null` pour un ouvrier.
 * Le frontend ne décide jamais qui voit le budget, il met en forme ce qu'il reçoit.
 */
export function InformationsChantier({ chantier }: InformationsChantierProps) {
  const { adresse } = chantier;

  return (
    <Carte>
      <Texte>{`${adresse.voie}, ${adresse.code_postal} ${adresse.ville}`}</Texte>
      <Texte variante="secondaire">{`Client : ${chantier.client}`}</Texte>
      <Texte variante="secondaire">
        {`Du ${formaterDate(chantier.date_debut)} au ${formaterDate(chantier.echeance)}`}
      </Texte>
      {chantier.budget !== null && (
        <Texte variante="secondaire">{`Budget : ${formaterMontant(chantier.budget)}`}</Texte>
      )}
    </Carte>
  );
}
