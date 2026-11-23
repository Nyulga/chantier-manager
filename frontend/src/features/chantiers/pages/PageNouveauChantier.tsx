// Page « nouveau chantier » (adresse `/chantiers/nouveau`) : le formulaire de création.
import { useNavigate } from 'react-router';

import { Alerte, Lien, Pile, Texte, Titre } from '@/ui';

import { FormulaireChantier } from '../components/FormulaireChantier';
import { useCreerChantier } from '../services/useCreerChantier';
import { usePeutCreerChantier } from '../services/usePeutCreerChantier';

/**
 * Écran de création. Le formulaire n'est affiché que si l'API annonce le droit de créer un
 * chantier : un ouvrier lit une information à la place, sans jamais voir de formulaire inutile
 * (même pas pendant le chargement de ses droits). Après le succès, on arrive sur le détail du
 * chantier créé.
 */
export function PageNouveauChantier() {
  const peutCreer = usePeutCreerChantier();
  const creation = useCreerChantier();
  const naviguer = useNavigate();

  return (
    <Pile>
      <Lien vers="/chantiers">Retour aux chantiers</Lien>
      <Titre niveau={1}>Nouveau chantier</Titre>
      {peutCreer.isPending && <Texte variante="secondaire">Chargement…</Texte>}
      {peutCreer.isError && <Alerte>{peutCreer.error.message}</Alerte>}
      {peutCreer.data === false && <Texte>Ton profil ne permet pas de créer un chantier.</Texte>}
      {peutCreer.data === true && (
        <FormulaireChantier
          enCours={creation.isPending}
          erreur={creation.error}
          onSoumettre={(saisie) => {
            creation.mutate(saisie, {
              onSuccess: (chantier) => void naviguer(`/chantiers/${chantier.id}`),
            });
          }}
        />
      )}
    </Pile>
  );
}
