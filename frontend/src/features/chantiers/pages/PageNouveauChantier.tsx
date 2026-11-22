// Page « nouveau chantier » (adresse `/chantiers/nouveau`) : le formulaire de création.
import { useNavigate } from 'react-router';

import { Alerte, Lien, Pile, Titre } from '@/ui';

import { FormulaireChantier } from '../components/FormulaireChantier';
import { useCreerChantier } from '../services/useCreerChantier';

/** Écran de création. Après le succès, on arrive sur le détail du chantier créé. */
export function PageNouveauChantier() {
  const creation = useCreerChantier();
  const naviguer = useNavigate();

  return (
    <Pile>
      <Lien vers="/">Retour aux chantiers</Lien>
      <Titre niveau={2}>Nouveau chantier</Titre>
      {creation.isError && <Alerte variante="erreur">{creation.error.message}</Alerte>}
      <FormulaireChantier
        enCours={creation.isPending}
        onSoumettre={(saisie) => {
          creation.mutate(saisie, {
            onSuccess: (chantier) => void naviguer(`/chantiers/${chantier.id}`),
          });
        }}
      />
    </Pile>
  );
}
