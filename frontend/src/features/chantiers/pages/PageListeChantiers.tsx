// Page « liste des chantiers » (adresse `/`) : une carte par chantier visible par l'acteur.
import { Alerte, Lien, Pile, Texte, Titre } from '@/ui';

import { CarteChantier } from '../components/CarteChantier';
import { useChantiers } from '../services/useChantiers';
import { useProfilCourant } from '../services/useProfilCourant';

/** Écran de la liste. Les chantiers affichés sont ceux que l'API renvoie pour le profil choisi. */
export function PageListeChantiers() {
  const chantiers = useChantiers();
  const profil = useProfilCourant();

  return (
    <Pile>
      <Titre niveau={2}>Chantiers</Titre>
      {profil === 'chef' && <Lien vers="/chantiers/nouveau">Nouveau chantier</Lien>}
      {chantiers.isPending && <Texte variante="secondaire">Chargement des chantiers…</Texte>}
      {chantiers.isError && <Alerte variante="erreur">{chantiers.error.message}</Alerte>}
      {chantiers.data?.length === 0 && <Texte>Aucun chantier pour le moment.</Texte>}
      {chantiers.data?.map((chantier) => (
        <CarteChantier key={chantier.id} chantier={chantier} />
      ))}
    </Pile>
  );
}
